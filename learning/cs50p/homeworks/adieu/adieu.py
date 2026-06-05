names=[]
while True:
    try:
        name=input("Name: ")
        names.append(name)
    except EOFError:
        break
print()
print('Adieu, adieu, to ', end='')
for i in range(len(names)):
    if i==0:
        print(names[i],end='')
    elif i==len(names)-1:
        if len(names)==2:
            print(' and '+names[i])
        else:
            print(', and '+names[i])
    else:
        print(', '+names[i],end='')
