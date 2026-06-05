import random


def main():
    n=get_level()
    right=0
    for _ in range(10):
        X=generate_integer(n)
        Y=generate_integer(n)
        print(f'{X} + {Y} = ',end='')
        err=0
        while True:
            if err==3:
                print(f'{X} + {Y} = {X+Y}')
                break
            try:
                Z=int(input())
                if Z!=X+Y:
                    print('EEE')
                    err+=1
                else:
                    right+=1
                    break
            except ValueError:
                print('EEE')
                err+=1
    print(right)


def get_level():
    while True:
        try:
            n=int(input())
            if n not in [1,2,3]:
                continue
            return n
        except ValueError:
            continue


def generate_integer(level):
    if level==1:
        return random.randint(0,9)
    if level==2:
        return random.randint(10,99)
    if level==3:
        return random.randint(100,999)


if __name__ == "__main__":
    main()
