#!/usr/bin/python

import sys
import random
import math

# actually, this should be called "is pseudoprime", but its safe enough
def isprime(n):
    sp = set([2,3,5,7,11,13,17,19])
    if n < 20: return (n in sp)
    for b in sp:
        if pow(b,n-1,n) != 1:
            return False
    return True

# Jacobi-Symbol, implementation taken directly from wikipedia
def jacobi(k,n):
    k,n=n,k # wikipedia got it wrong
    assert(k % 2 == 1)
    n = n % k
    t = 1
    while n != 0:
        while n % 2 == 0:
            n //= 2
            r = k % 8
            if r == 3 or r == 5:
                t = -t
        n,k = k,n
        if n % 4 == 3 and k % 4 == 3:
            t = -t
        n = n % k
    if k == 1:
        return t
    return 0

assert([jacobi(k,5) for k in range(1,5)] == [1,-1,-1,1])
assert([jacobi(k,7) for k in range(1,7)] == [1,1,-1,1,-1,-1])
assert([jacobi(k,9) for k in range(1,9)] == [1,1,0,1,1,0,1,1])
assert([jacobi(k,11) for k in range(1,11)] == [1,-1,1,1,1,-1,-1,-1,1,-1])
assert([jacobi(k,15) for k in range(1,15)] == [1,1,0,1,0,0,-1,1,0,0,-1,0,-1,-1])

def factorize(n):
    if n >= 10**60:
        FATAL(f"Cannot factor {n}, it is too large.")
        assert(False)
    # stop recursion if prime is found
    if isprime(n):
        return [n]
    # I don't want to implement a fancy algorithm either.
    # So we just use some TF and then pollard rho...
    for i in [2,3,5,7,11,13,17,19,23,29,31,37,39]:
        if n % i == 0:
            return [i] + factorize(n//i)
    # pollard rho
    while True:
        x = random.randrange(3,n,2)
        y = x
        while True:
            x = pow(x,2,n) + 1
            y = pow(y,2,n) + 1
            y = pow(y,2,n) + 1
            p = math.gcd(x-y,n)
            if p == n:
                break # try with different start values
            elif p != 1:
                # we found a (potentially composite) factor!
                return sorted(factorize(n//p) + factorize(p))


def genprimes(start, end):
    primes = set()
    while len(primes) < 100:
        candidate = random.randrange(start, end)
        if isprime(candidate):
            primes.add(candidate)
    return sorted(list(primes))

def is_smooth(factors, B1, B2):
    factors = sorted(factors)
    if factors[-1] > B2:
        return False
    if factors[-2] > B1:
        return False
    return True



def main(argv):
    B1 = int(argv[1])
    B2 = int(argv[2])
    assert(B1 < B2 and B1 >= 1000 and B2>=2*B1)

    # generate primes in relevant ranges first
    small  = genprimes(2,   B1) 
    medium = genprimes(B1+1,B2)

    # now we try to find primes p where p-1 is B1/B2 smooth   
    both = set()
    pminus = set()
    pplus = set()
    while len(pminus) < 100 or len(pplus) < 100 or len(both) < 100:
        a,b,c = random.choice(small), random.choice(small), random.choice(medium)
        candidate = 2*a*b*c 
        if isprime(candidate+1): # P-1 is smooth
            #print(f"found P-1 smooth prime 2*{a}*{b}*{c}+1 = {candidate+1}")
            f = factorize(candidate+2)
            if is_smooth(f,B1,B2):
                #print(f"-> P+1 smooth! (factors are: {f})")
                both.add(candidate+1)
            else:
                #print(f"-> NOT P+1 smooth! (factors are: {f})")
                pminus.add(candidate+1)
        if isprime(candidate-1):
            #print(f"found P+1 smooth prime 2*{a}*{b}*{c}+1 = {candidate-1}")
            f = factorize(candidate-2)
            if is_smooth(f,B1,B2):
                #print(f"-> P-1 smooth! (factors are: {f})")
                both.add(candidate-1)
            else:
                #print(f"-> NOT P-1 smooth! (factors are: {f})")
                pplus.add(candidate-1)

    #print("-------------------------------------------------------------")
    #print("Now trying to find non-smooth numbers")
    none = set()
    candidate_lower = 2 * (B1 // 4) * (B1 // 4) * (B1 + (B2-B1) // 4) 
    candidate_upper = 2 * (B1 * 3 // 2) * (B1 * 3 // 2) * (B1 + (B2-B1) *3 // 2)
    while len(none) < 100:
        candidate = random.randrange(candidate_lower, candidate_upper)
        # we start somewhere in the middle of the range
        if isprime(candidate):
            #print(f"current candidate {candidate}")
            fminus = factorize(candidate-1)
            if is_smooth(fminus, 2*B1, 4*B2):
                #print(f"-> P-1 smooth! (factors are: {f})")
                pass
            else:
                fplus = factorize(candidate + 1)
                if is_smooth(fplus, 2*B1, 4*B2):
                    #print(f"-> P+1 smooth! (factors are: {f})")
                    pass
                else:
                    #print(f"-> both P+-1 unsmooth (factors P-1 / P+1 are: {fminus}, {fplus})")
                    none.add(candidate)
            #print(f"--------------------------------------------------")

    none   = sorted(list(none))
    pminus = sorted(list(pminus))
    pplus  = sorted(list(pplus))
    both   = sorted(list(both))
    def list2str(l):
        return ' '.join([str(i) for i in l])
    #print(f"NOT P-1 smooth, NOT P+1 smooth:   {list2str(none)}")
    #print(f"    P-1 smooth, NOT P+1 smooth:   {list2str(pminus)}")
    #print(f"NOT P-1 smooth,     P+1 smooth:   {list2str(pplus)}")
    #print(f"    P-1 smooth,     P+1 smooth:   {list2str(both)}")


    def min_B1B2(factors):
        factors = sorted(factors)
        if len(factors) == 1: 
            return (factors[0],factors[0])
        return (factors[-2], factors[-1])
    def print_B1B2_bounds(p1, p2):
        print(f"-> P-1 of p1 requires (B1,B2) = {min_B1B2(factorize(p1-1))}")
        print(f"-> P+1 of p1 requires (B1,B2) = {min_B1B2(factorize(p1+1))}")
        print(f"-> P-1 of p2 requires (B1,B2) = {min_B1B2(factorize(p2-1))}")
        print(f"-> P+1 of p2 requires (B1,B2) = {min_B1B2(factorize(p2+1))}")

    print(f"(P-1 P+1) (P-1 P+1) smooth?") 
    print(f"---------------------------")
    for i in range(1):
        # take a very large prime
        p1 = random.choice(none)
        p2 = random.choice(none)
        print(f"(no  no ) (no  no ) {p1*p2} = {p1} * {p2}")
        print_B1B2_bounds(p1,p2)
        
        p1 = random.choice(none)
        p2 = random.choice(pminus)
        print(f"(no  no ) (yes no ) {p1*p2} = {p1} * {p2}")
        print_B1B2_bounds(p1,p2)
        p1 = random.choice(pminus)
        p2 = random.choice(pminus)
        print(f"(yes no ) (yes no ) {p1*p2} = {p1} * {p2}")
        print_B1B2_bounds(p1,p2)

        p1 = random.choice(none)
        p2 = random.choice(pplus)
        print(f"(no  no ) (no  yes) {p1*p2} = {p1} * {p2}")
        print_B1B2_bounds(p1,p2)
        p1 = random.choice(pminus)
        p2 = random.choice(pplus)
        print(f"(yes no ) (no  yes) {p1*p2} = {p1} * {p2}")
        print_B1B2_bounds(p1,p2)
        p1 = random.choice(pplus)
        p2 = random.choice(pplus)
        print(f"(no  yes) (no  yes) {p1*p2} = {p1} * {p2}")
        print_B1B2_bounds(p1,p2)
        
        p1 = random.choice(none)
        p2 = random.choice(both)
        print(f"(no  no ) (yes yes) {p1*p2} = {p1} * {p2}")
        print_B1B2_bounds(p1,p2)
        p1 = random.choice(pminus)
        p2 = random.choice(both)
        print(f"(yes no ) (yes yes) {p1*p2} = {p1} * {p2}")
        print_B1B2_bounds(p1,p2)
        p1 = random.choice(pplus)
        p2 = random.choice(both)
        print(f"(no  yes) (yes yes) {p1*p2} = {p1} * {p2}")
        print_B1B2_bounds(p1,p2)
        p1 = random.choice(both)
        p2 = random.choice(both)
        print(f"(yes yes) (yes yes) {p1*p2} = {p1} * {p2}")
        print_B1B2_bounds(p1,p2)
        
main(sys.argv)

