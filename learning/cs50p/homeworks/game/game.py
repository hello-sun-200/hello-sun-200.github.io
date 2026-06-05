import random
while True:
    try:
        n=int(input('Level: '))
        if n<1:
            continue
        break
    except ValueError:
        continue
r=random.randint(1,n)
while True:
    try:
        guess=int(input('Guess: '))
        if guess<1:
            continue
        if guess==r:
            print('Just right!')
            break
        elif guess<r:
            print('Too small!')
        else:
            print('Too large!')
    except ValueError:
        continue

