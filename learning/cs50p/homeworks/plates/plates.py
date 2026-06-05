def main():
    plate = input("Plate: ")
    if is_valid(plate):
        print("Valid")
    else:
        print("Invalid")


def is_valid(s):
    if len(s)>6 or len(s)<2:
        return False
    if not s[:2].isalpha():
        return False
    for i in range(len(s)):
        if s[i].isnumeric():
            if s[i]=='0':
                return False
            if not s[:i].isalpha():
                return False
            if not s[i:].isnumeric():
                return False
            break
    return True


main()
