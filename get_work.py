#!/usr/bin/python

import sys
import re
import time
import urllib3
import datetime
import math
http = urllib3.PoolManager(headers={"User-Agent":"keisentraut/prime95-optimal-worktodo"})

# print error message and exit hard
def FATAL(msg):
    print(f"FATAL: {msg}")
    sys.exit(1)

PRINT_DEBUG=1
def DEBUG(msg):
    if PRINT_DEBUG:
        print(f"# {msg}")

# prints usage
def usage():
    DEBUG("This is a script which queries the PrimeNet server in order ")
    DEBUG("to get the status of exponents. Please don't run this with ")
    DEBUG("large ranges, it might create high load on the server.")
    DEBUG("")
    DEBUG("see https://mersenneforum.org/showthread.php?t=26750")
    DEBUG("")
    DEBUG("usage:")
    DEBUG("    python.exe get_work.py <from> <to> <print_debug>")
    DEBUG("example:")
    DEBUG("    python.exe get_work.py 123000 124000 True")
    DEBUG("        generates P-1/P+1 worktodo.txt file for Mersenne numbers with exponents between")
    DEBUG("        123000 and 124000.If all Mersenne numbers in this range have appropriate P-1/P+1,")
    DEBUG("        then no output is generated. The last argument \"True\" enables debug output.")
    DEBUG("        Set the debug output to False, if you want to pass the output directly to Prime95.")


# Bounds defined by gut feeling.
# see also posting by ATH at https://mersenneforum.org/showthread.php?t=26750 where he suggests:
#
#	      No known factors	     With known factors
#Exponent       P-1 B1  P+1 B1          P-1 B1  P+1 B1
#50K-250K 	100M	50M		30M 	15M
#250K-500K	 30M	15M		15M	 8M
#500K-1M		 15M	 8M		10M	 5M
#
def PM1_B1_should(n, known_factors=False):
    if known_factors == False:
        if n<  100000: return 250000000
        if n<  250000: return 100000000
        if n<  500000: return  30000000
        if n< 1000000: return  15000000
        if n< 4000000: return   5000000
        if n<10000000: return   2500000
        return                  2000000
    else:
        if n<  100000: return 100000000
        if n<  250000: return  30000000
        if n<  500000: return  15000000
        if n< 1000000: return  10000000
        if n< 4000000: return   5000000
        if n<10000000: return   2500000
        return                  2000000
        
def PP1_B1_should(n, known_factors=False):
    # half of P-1 bound
    return PM1_B1_should(n, known_factors) // 2

# actually, this should be called "is pseudoprime", but its safe enough
def isprime(n):
    sp = set([2,3,5,7,11,13,17,19])
    if n < 20: return (n in sp)
    for b in sp:
        if pow(b,n-1,n) != 1:
            return False
    return True

ECMBOUNDS = [  (11000,100,20), \
                (50000,280,25), \
                (250000,640,30), \
                (1000000,1580,35), \
                (3000000,4700,40), \
                (11000000,9700,45), \
                (44000000,17100,50), \
                (110000000,46500,55), \
                (260000000,112000,60), \
                (800000000,360000,65)]
def get_ecm_level(ecm):
    level = 0 # number of digits
    for minB1, desired, digits in ECMBOUNDS:
        count = 0
        for (B1, B2) in ecm:
            if B1 >= minB1:
                count += ecm[(B1,B2)]
        count = count / desired
        if count >= 2.:
            # twice as many curves as required
            # chance to miss factor is exp(-2) = 0.1353352832366127
            # therefore, increase digits by 1
            level = max(level, digits+1)
        elif count >= 1.:
            # exactly as many curves as required
            # chance to miss factor is exp(-1) = 0.36787944117144233 
            level = max(level, digits)
        elif count >= 0.5:
            # half of curves required
            # chance to miss factor is exp(-0.5) = 0.6065306597126334 
            # therefore, reduce digits by 3 
            level = max(level, digits-3)
    return level

# returns t30 B1 bound where you should continue when having t25 completed
def ecm_level_to_B1(level):
    B1 = 1000000000000 # larger than any reasonable B1 bound
    for minB1, desired, digits in ECMBOUNDS:
        if level < digits:
            B1 = min(B1, minB1)
    return B1
            

def worktodo_PM1(n,B1,B2=None, how_far_factored=67, factors=[]):
    assert(B1 >= 11000)
    if factors:
        factors = ",\"" + ",".join([str(f) for f in factors]) + "\""
    else:
        factors = ""
    if B2:
        assert(B1 <= B2 and B2 <= 100000 * B1)
    else:
        B2 = 0
    return f"Pminus1=N/A,1,2,{n},-1,{B1},{B2},{how_far_factored}" + factors

def worktodo_PP1(n,B1,B2=None,nth_run=1, how_far_factored=67, factors=[]):
    assert(B1 >= 11000)
    if factors:
        factors = ",\"" + ",".join([str(f) for f in factors]) + "\""
    else:
        factors = ""
    if B2:
        assert(B1 <= B2 and B2 <= 100000 * B1)
    else:
        B2 = 0
    return f"Pplus1=N/A,1,2,{n},-1,{B1},{B2},{nth_run},{how_far_factored}" + factors

#############################################################################################3

if len(sys.argv) < 3 or len(sys.argv) > 4:
    usage()
    sys.exit(1)
else:
    start = int(sys.argv[1])
    stop  = int(sys.argv[2])
    if len(sys.argv) == 4:
        PRINT_DEBUG = int(sys.argv[3])

sleep_time = 1.

for n in range(start,stop):
    if isprime(n):
        if n < 50000:
            DEBUG(f"You should use GMP-ECM for this. Ignoring M{n}.")
            continue

        response = http.request('GET', f"https://www.mersenne.org/report_exponent/?exp_lo={n}&exp_hi=&text=1&full=1&ecmhist=1")   
        html = response.data.decode('utf-8')
        lines = [l.strip() for l in html.split("\n") if l.strip().startswith(f"{n}\t")]
        factors = set()
        ecm = {}    # (B1, B2) : count
        pm1 = set() # (B1, B2, E)
        pp1 = set() # (B1, B2, start1, start2)
        is_recently_assigned = False
        is_fully_factored = False
        how_far_factored = [True] * 64 + [False] * (100-64) # how_far_factored[i] indicates if [2^(i-1); 2^(i)] was done
        for l in lines:
            if l.startswith(f"{n}\tFactored\t"):
                #41681   Factored        1052945423;16647332713153;2853686272534246492102086015457
                factors |= set([int(f) for f in l.split("\t")[2].split(";")])
            elif l.startswith(f"{n}\tPRPCofactor\t"):
                #41681   PRPCofactor     Verified (Factored);2017-11-09;kkmrkkblmbrbk;PRP_PRP_PRP_PRP_;3;37261;1;3
                pass
            elif l.startswith(f"{n}\tUnfactored\t"):
                #100000007	Unfactored	2^79
                result = l.split("\t")[2]
                assert(result.startswith("2^"))
                high = int(result[2:])
                for i in range(high):
                    how_far_factored[i] = True
            elif l.startswith(f"{n}\tLL\t"):
                # 100000007	LL	Verified;2018-02-26;G0rfi3ld;F9042256B193FAA0;3178317
                pass 
            elif l.startswith(f"{n}\tPRP\t"):
                # 20825573	PRP	Verified;2020-10-12;gLauss;738AD2BB0D72E3AA;1276614;1;3
                pass
            elif l.startswith(f"{n}\tPM1\t"):
                #100000007	PM1	B1=5000000,B2=150000000
                result = l.split("\t")[2]
                if   m:= re.match("^B1=([0-9]*),B2=([0-9]*),E=([0-9]*)$", result):
                    B1, B2, E = int(m.group(1)), int(m.group(2)), int(m.group(3))
                elif m:= re.match("^B1=([0-9]*),B2=([0-9]*)$", result):
                    B1, B2 = int(m.group(1)), int(m.group(2))
                    E = 0
                elif m:= re.match("^B1=([0-9]*)$", result):
                    B1 = int(m.group(1))
                    B2, E = B1, 0
                else:
                    FATAL(f"could not parse PM1 result \"{result}\" in line \"{l}\"")
                assert(B1 <= B2)
                assert(E in [0,6,12,30,48])
                pm1.add( (B1,B2,E))
            elif l.startswith(f"{n}\tAssigned\t"):
                h = l.split("\t")[2].split(";")
                # 41081	Assigned	2017-10-09;Chang Chia-Tche;PRP test;;0.0;updated on 2017-10-09;expired on 2017-10-13
                age_days = (datetime.datetime.now() - datetime.datetime.strptime(h[0], "%Y-%m-%d")).days
                if age_days <= 2*365:
                    is_recently_assigned = True
            elif l.startswith(f"{n}\tHistory\t"):
                h = l.split("\t")[2].split(";")
                worktype, result = h[2], h[3]
                if worktype == "F-ECM" or worktype == "F":
                    # 41681   History 2015-04-26;Serge Batalov;F-ECM;Factor: 2853686272534246492102086015457
                    # 41681   History 2008-08-26;-Anonymous-;F;Factor: 16647332713153
                    factors.add(int(result.split(" ")[1]))
                elif worktype == "CERT" or worktype == "C-PRP" or worktype == "C-LL":
                    # we don't care for factorization purposes
                    pass
                elif worktype == "NF":
                    # 100000007	History	2007-07-04;ComputerraRU;NF;no factor to 2^50
                    if   m:= re.match("^no factor from 2\^([0-9]*)[ ]*to 2\^([0-9]*)[ ]*$", result):
                        low, high = int(m.group(1)), int(m.group(2))
                        for i in range(low, high):
                            how_far_factored[i] = True
                    elif m:= re.match("^no factor to 2\^([0-9]*)$", result):
                        high = int(m.group(1))
                        for i in range(high):
                            how_far_factored[i] = True
                    else:
                        FATAL(f"could not parse NF result \"{result}\" in line \"{l}\"")
                        assert(False)
                elif worktype == "NF-ECM":
                    # 41681   History 2011-01-23;James Hintz;NF-ECM;3 curves, B1=250000, B2=25000000
                    if   m:=re.match("^([0-9]*) curve[s]?, B1=([0-9]*), B2=([0-9]*)$", result):
                        c  = int(m.group(1))
                        B1 = int(m.group(2))
                        B2 = int(m.group(3))
                    elif m:=re.match("^([0-9]*) curve[s]?, B1=([0-9]*)", result):
                        c  = int(m.group(1))
                        B1 = int(m.group(2))
                        B2 = B1
                    else:
                        FATAL(f"could not parse NF-ECM result \"{result}\" in line \"{l}\"")
                        assert(False)
                    assert(B1 <= B2)
                    assert(c >= 0) # actually, there are entries where count == 0
                    if (B1,B2) not in ecm: ecm[(B1,B2)] = 0
                    ecm[(B1,B2)] += c
                elif worktype == "NF-PM1":
                    # 3999971	History	2018-12-21;Jocelyn Larouche;NF-PM1;B1=3999971, B2=399997100, E=12
                    if   m:= re.match("^B1=([0-9]*), B2=([0-9]*), E=([0-9]*)$", result):
                        B1, B2, E = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    elif m:= re.match("^B1=([0-9]*), B2=([0-9]*)$", result):
                        B1, B2 = int(m.group(1)), int(m.group(2))
                        E = 0
                    elif m:= re.match("^B1=([0-9]*)$", result):
                        B1 = int(m.group(1))
                        B2, E = B1, 0
                    else:
                        FATAL(f"could not parse NF-PM1 result \"{result}\" in line \"{l}\"")
                        assert(False)
                    assert(B1 <= B2)
                    assert(E in [0,6,12,30,48])
                    pm1.add( (B1,B2,E))
                elif worktype == "F-PM1":
                    # 123031	History	2013-08-29;BloodIce;F-PM1;Factor: 3158950722867400921
                    # 2000177	History	2019-01-15;Jocelyn Larouche;F-PM1;Factor: 131059942116526306804441369 / (P-1, B1=1000000) 
                    if   m:= re.match("^Factor: ([0-9]*)$", result):
                        f = int(m.group(1))
                        factors.add(f)
                    elif m:= re.match("^Factor: ([0-9]*) / \(P-1, B1=([0-9]*)\)$", result):
                        f, B1 = int(m.group(1)), int(m.group(2))
                        B2, E = B1, 0
                        pm1.add( (B1,B2,E) )
                        factors.add(f)
                    elif m:= re.match("^Factor: ([0-9]*) / \(P-1, B1=([0-9]*), B2=([0-9]*)\)$", result):
                        f, B1, B2 = int(m.group(1)), int(m.group(2)), int(m.group(3))
                        E = 0
                        pm1.add( (B1,B2,E) )
                        factors.add(f)
                    elif m:= re.match("^Factor: ([0-9]*) / \(P-1, B1=([0-9]*), B2=([0-9]*), E=([0-9]*)\)$", result):
                        f, B1, B2, E = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
                        pm1.add( (B1,B2,E) )
                        factors.add(f)
                    else:
                        FATAL(f"Could not parse F-PM1 result \"{result}\" in line \"{l}\"")
                        assert(False)
                elif worktype == "F-PP1":
                    if   m:= re.match("^Start=([0-9]*)/([0-9]*), B1=([0-9]*), B2=([0-9]*), Factor: ([0-9]*)$", result):
                        start1, start2, B1, B2, f = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))
                        factors.add(f)
                        assert(B1 <= B2)
                        pp1.add( (B1, B2, start1, start2) )
                    else:
                        FATAL(f"could not parse NF-PP1 result \"{result}\" in line \"{l}\"")
                        assert(False)
                elif worktype == "NF-PP1":
                    # 41017	History	2021-04-27;gLauss;NF-PP1;Start=2/7, B1=10000000, B2=1000000000
                    if   m:= re.match("^Start=([0-9]*)/([0-9]*), B1=([0-9]*), B2=([0-9]*)$", result):
                        start1, start2, B1, B2 = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
                    elif m:= re.match("^Start=([0-9]*)/([0-9]*), B1=([0-9]*)$", result):
                        start1, start2, B1 = int(m.group(1)), int(m.group(2)), int(m.group(3))
                        B2 = B1
                    else:
                        FATAL(f"could not parse NF-PP1 result \"{result}\" in line \"{l}\"")
                        assert(False)
                    assert(B1 <= B2)
                    pp1.add( (B1, B2, start1, start2) )
                else:
                    FATAL(f"unknown worktype {worktype}")
                    assert(False)
            else:
                FATAL(f"could not parse line \"{l}\"")
                assert(False)
        # check if factors are actually correct:
        for f in factors:
            assert(pow(2,n,f) == 1)
        # for small numbers, we also check if fully factored
        # TODO: improve this, it is not considering probable prime factors (PRP-CF)
        if n <= 50000:
            remaining = 2**n-1
            for f in factors:
                remaining //= f
            # check if fully factored
            if remaining == 1:
                is_fully_factored = True
            elif isprime(remaining):
                is_fully_factored = True
                factors.add(remaining)
        # convert how_far_factored from a bit array to an integer
        # please note that TJAOI factored everything up to 66 bit
        for i in range(66): how_far_factored[i] = True
        hff = 0
        while how_far_factored[hff]: hff += 1
        how_far_factored = hff

        # use ECM bounds to adapt how_far_factored
        # as ECM is probabilistic, we want to be conservative and remove an extra 12 bits / 4 digits of factor size
        ecm_level = get_ecm_level(ecm)
        ecm_factored = int(ecm_level * math.log2(10)) - 12
        if how_far_factored < ecm_factored:
            DEBUG(f"increased how_far_factored from {how_far_factored} to {ecm_factored} because of substantial ECM")
            how_far_factored = ecm_factored
        
        # B1 should be chosen accordingly, if you have done TF very high, you should start with larger bound 
        # e.g. TF = 80 makes ECM t20 useless
        ECM_B1 = ecm_level_to_B1(ecm_level)
        ECM_B1 = max(ECM_B1, ecm_level_to_B1(int(how_far_factored / math.log2(10))))

        # hard cut off at 99, because prime95 cannot do larger
        how_far_factored = min(how_far_factored, 99)
       
        # boolean
        if factors:
            factors_known = True
        else:
            factors_known = False

        # debug output
        DEBUG(f"n:                {n}")
        DEBUG(f"how_far_factored: {how_far_factored}")
        DEBUG(f"Factors:          {factors}")
        DEBUG(f"factors known:    {factors_known}")
        DEBUG(f"ECM Factoring:    {ecm}")
        DEBUG(f"ECM level:        t{ecm_level}")
        DEBUG(f"ECM current B1:   {ECM_B1}")
        DEBUG(f"P-1 Factoring:    {pm1}")
        DEBUG(f"P+1 Factoring:    {pp1}")
        DEBUG(f"assigned:         {is_recently_assigned}")
        DEBUG(f"fully factored:   {is_fully_factored}")
        DEBUG(f"")


        #####################################################################
        # now the interesting part where the calculation what to do is done
        #####################################################################

        # only do P-1 / P+1 assigments, if B1 bound will increase by at least this factor
        # If it is set to 2 and P-1 was done until 10M, then no new 15M assignment will be generated
        DUPLICATE_WORK_FACTOR_PROPER_STAGE2 = 2.
        DUPLICATE_WORK_FACTOR_NO_STAGE2     = 1.3

        # recently assigned or fully factored exponents will be skipped
        if is_recently_assigned:
            DEBUG("skipping this exponent, because there is a recent assignment")
            continue
        if is_fully_factored:
            DEBUG("skipping this exponent, because it is fully factored")
            continue

        # calculate bounds
        PM1_B1 = PM1_B1_should(n, factors_known)
        PP1_B1 = PP1_B1_should(n, factors_known)
        # if substantial ECM is already done, we might want to increase those bounds!
        if ecm:
            if 20*ECM_B1 > PM1_B1:
                DEBUG(f"increased desired P+1 B1 to 20*ECM_B1 because current ECM bound is already at B1={ECM_B1}") 
                PM1_B1 = 20*ECM_B1
            if 10*ECM_B1 > PP1_B1:
                DEBUG(f"increased desired P+1 B1 to 10*ECM_B1 because current ECM bound is already at B1={ECM_B1}") 
                PP1_B1 = 10*ECM_B1

        # check if it needs P-1 factoring
        should_do_pm1 = True
        B1_max_PM1 = 0 # will be required for calculating P+1 bounds
        for (B1, B2, E) in pm1:
            B1_max_PM1 = max(B1_max_PM1, B1) 
            # don't do P-1 again if there was a proper run already
            if B2 / B1 >= 10 and B1 > PM1_B1 / DUPLICATE_WORK_FACTOR_PROPER_STAGE2:
                DEBUG(f"should not do P-1: B1={PM1_B1} recommended but {B1} already done with B2={B2/B1:.1f}*B1")
                should_do_pm1 = False 
            elif B1 > PM1_B1 / DUPLICATE_WORK_FACTOR_NO_STAGE2:
                DEBUG(f"should not do P-1: B1={PM1_B1} recommended but {B1} already done (albeit without stage2)")
                should_do_pm1 = False 
        if should_do_pm1:
            print(worktodo_PM1(n,PM1_B1,how_far_factored=how_far_factored,factors=factors))

        # check if it needs P+1 factoring
        should_do_pp1 = True
        B1_max_start1_2 = 0
        B1_max_start1_6 = 0
        if B1_max_PM1//2 > PP1_B1:
            PP1_B1 = B1_max_PM1 // 2
            DEBUG(f"increased desired P+1 B1 to {PP1_B1} which is half of the already done P-1 bound")
        for (B1, B2, start1, start2) in pp1:
            # update B1 bound for start values 2 and 6
            if start1 == 2:
                B1_max_start1_2 = max(B1_max_start1_2, B1)
            elif start1 == 6:
                B1_max_start1_6 = max(B1_max_start1_6, B1)
            # ignore it, if there was a proper P+1 run with or without stage 2
            if B2 / B1 > 10 and B1 > PP1_B1 / DUPLICATE_WORK_FACTOR_PROPER_STAGE2:
                DEBUG(f"should not do PP1: B1={PP1_B1} recommended but {B1} already done with B2={B2/B1:.1f}*B1")
                should_do_pp1 = False 
            elif B1 > PP1_B1 / DUPLICATE_WORK_FACTOR_NO_STAGE2:
                DEBUG(f"should not do PP1: B1={PP1_B1} recommended but {B1} already done (albeit without stage2)")
                should_do_pp1 = False 
        if should_do_pp1:
            # determine if we should use 2, 6 or a random value as start values
            # we want to use random only if there has been no 2 or 6 run before because they have higher likelyhood
            nth_run = 3 # random
            if B1_max_start1_2 == 0:
                nth_run = 1
            elif B1_max_start1_6 == 0:
                nth_run = 2
            else:
                # in degenerate cases where there was a run with the optimal values 2 or 6 run,
                # but only to very low bounds, we still want to use it.
                if B1_max_start1_2 < PP1_B1 * 0.01:
                    nth_run = 1
                elif B1_max_start1_6 < PP1_B1 * 0.01:
                    nth_run = 2
            print(worktodo_PP1(n,PP1_B1,B2=0,nth_run=nth_run,how_far_factored=how_far_factored,factors=factors))

        # sleep in order to not stress the server
        time.sleep(sleep_time)
