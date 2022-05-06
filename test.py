import math

def bessel(x,n,N):

    q = 0

    for r in range(N):
        taylor_term = (((-1)**r)*(x/2)**(2*r+n))
        taylor_term = taylor_term/(math.factorial(r)*math.factorial(n+r))
        q = q + taylor_term

    print(q)

    return q

bessel(4,1,70)

def selfDividingNumbers(left, right):
    # simplest poss solution is to check all cases
    # go through each elem in list and check if a % each of its digits is 0

    self_dividing_nums = list(range(left, right + 1))

    for i in self_dividing_nums:  # loop through all elems
        string_i = str(i)  # convert int to string
        if '0' in string_i:  # eliminate i iff it contains 0
            self_dividing_nums.remove(i)
        else:
            for j in string_i:
                digit = int(j)  # eliminate i if it has a digit which is not a divisor
                if i % digit != 0:
                    self_dividing_nums.remove(i)
                    break

    return self_dividing_nums

def is_smaller(s, t):
    # checks if s < t lexicographically and if so returns a 1, else 0
    # e.g. s = 'adbc' , t = 'bcad'

    first_diff = 0


    for i in range(len(s)):
        if s[i] != t[i]:
            first_diff = i
            break

    return s[first_diff] < t[first_diff]