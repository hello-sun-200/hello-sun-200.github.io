import sys
if len(sys.argv) == 1:
    print("Too few command-line arguments")
    sys.exit(1)
elif len(sys.argv) > 2:
    print("Too many command-line arguments")
    sys.exit(1)
else:
    if sys.argv[1].strip().endswith('.py'):
        try:
            with open(sys.argv[1], "r") as py:
                cnt = 0
                for line in py.readlines():
                    if line.strip().startswith('\n') or line.strip().startswith('#') or len(line.strip())==0:
                        pass
                    else:
                        cnt += 1
                print(cnt)
        except FileNotFoundError:
            print("File does not exist")
    else:
        print("Not a Python File")
        sys.exit(1)
