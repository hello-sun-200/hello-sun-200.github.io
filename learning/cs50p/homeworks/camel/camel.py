name = input('camelCase: ')
lst=[]
for c in name:
    if c.isupper():
        lst.append('_')
        lst.append(c.lower())
    else:
        lst.append(c)
print(''.join(lst))
