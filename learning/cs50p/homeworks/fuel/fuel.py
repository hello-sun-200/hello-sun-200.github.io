while True:
    fraction = input("Fraction: ")
    try:
        fraction = fraction.split('/')
        n, d = int(fraction[0]), int(fraction[1])
        f = n/d
        if f < 0 or f > 1:
            continue
        if f >= 0.99:
            print('F')
        elif f <= 0.01:
            print('E')
        else:
            print(f'{round(f*100)}%')
        break
    except (ValueError, ZeroDivisionError):
        pass
