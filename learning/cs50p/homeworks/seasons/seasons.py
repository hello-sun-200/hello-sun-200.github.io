from datetime import date
import re
import sys
import inflect


def main():
    birth = input("YYYY-MM-DD: ").strip()
    pattern = r"^([0-9]{4})-([0-9]{2})-([0-9]{2})$"
    if match := re.search(pattern, birth):
        try:
            y = int(match.group(1))
            m = int(match.group(2))
            d = int(match.group(3))
            birth = date(y, m, d)
        except ValueError:
            sys.exit(1)
    else:
        sys.exit(1)
    today = date.today()
    minutes = round((today-birth).total_seconds()//60)
    minutes = inflect.engine().number_to_words(minutes)
    minutes = minutes.replace(" and ", " ").capitalize()+" minutes"
    print(minutes)


if __name__ == "__main__":
    main()
