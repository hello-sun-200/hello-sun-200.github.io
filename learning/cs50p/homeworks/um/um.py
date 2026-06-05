import re
import sys


def main():
    print(count(input("Text: ")))


def count(s):
    pattern=r"(^um\W+|\W+um$|^um$|\W+um\W+)"
    if match:=re.findall(pattern,s,re.IGNORECASE):
        return len(match)




if __name__ == "__main__":
    main()
