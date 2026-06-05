from pyfiglet import Figlet
import sys
import random
figlet = Figlet()
fonts=figlet.getFonts()
args=sys.argv
if len(args)==1:
    figlet.setFont(font=random.choice(fonts))
    print(figlet.renderText(input("Input")))
elif len(args)==3:
    if args[1]!='-f' and args[1]!='-font':
        print('Invalid usage')
        sys.exit(1)
    if args[2] not in fonts:
        print('Invalid usage')
        sys.exit(1)
    figlet.setFont(font=args[2])
    print(figlet.renderText(input()))
else:
    print('Invalid usage')
    sys.exit(1)
