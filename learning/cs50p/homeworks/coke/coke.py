amount = 50
while amount > 0:
    coin = int(input('Insert Coin: '))
    match coin:
        case 25 | 10 | 5:
            amount-=coin
        case _:
            pass
    print(f'Amount Due: {amount}')
print(f'Change Owed: {-amount}')
