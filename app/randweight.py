import random

# weighted random function
def randweight(vals):
    """
    Chooses alternative at random applying weigths for each alternative;
    values are given as a dict with {opt:weight}
    """
    wgtsum = sum(vals.values())
    randres = random.randint(1, wgtsum)
    check = 0
    for key in vals.keys():
        check += vals[key]
        if randres <= check: return key

# function to test that randweigth() works
def randtest(vals, num=5000):
    res = {key:0 for key in vals.keys()}
    for i in range(num):
        rand = randweight(vals)
        for key in vals.keys():
            if rand == key:
                res[key] += 1
    return res

if __name__ == '__main__':
    d = {'a':1, 'b':2, 'c':3}
    print(randtest(d))
