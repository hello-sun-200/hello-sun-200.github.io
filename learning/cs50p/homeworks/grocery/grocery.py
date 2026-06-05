grocery = {}

while True:
    try:
        item = input().upper()
        grocery[item] = grocery.get(item, 0) + 1
    except EOFError:
        lst = sorted(grocery.keys())
        for k in lst:
            print(grocery[k], k)
        exit(0)
