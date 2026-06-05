month = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]
while True:
    try:
        date = input("Date: ").strip()
        if date[0].isnumeric():
            date = date.split('/')
            y, m, d = int(date[2]), int(date[0]), int(date[1])
        else:
            date = date.split(', ')
            y = int(date[1])
            date = date[0].split(' ')
            d = int(date[1])
            m = month.index(date[0])+1
        if m < 0 or m > 12 or d < 0 or d > 31:
            continue
        print(f"{y}-{m:02}-{d:02}")
        break
    except IndexError:
        continue
