import re
import sys


def main():
    print(convert(input("Hours: ")))


def convert(s):
    # 改进的正则：严格匹配时分（包括 AM/PM）
    pattern = r"^(\d{1,2})(?::(\d{2}))? (AM|PM) to (\d{1,2})(?::(\d{2}))? (AM|PM)$"
    match = re.search(pattern, s)

    if not match:
        raise ValueError("Invalid time format")

    # 提取时间和 AM/PM 信息
    h1, m1, p1, h2, m2, p2 = match.groups()

    # 如果没有分钟，默认是 00 分钟
    m1 = m1 or "00"
    m2 = m2 or "00"

    # 检查分钟部分是否有效
    if int(m1) >= 60 or int(m2) >= 60:
        raise ValueError("Minutes must be less than 60")

    # 检查小时部分是否在有效范围
    h1 = int(h1)
    h2 = int(h2)

    if not (1 <= h1 <= 12):
        raise ValueError("Hour must be between 1 and 12 for AM/PM")
    if not (1 <= h2 <= 12):
        raise ValueError("Hour must be between 1 and 12 for AM/PM")

    # 转换 AM/PM 为 24 小时制
    if p1 == "PM" and h1 != 12:
        h1 += 12
    if p1 == "AM" and h1 == 12:
        h1 = 0

    if p2 == "PM" and h2 != 12:
        h2 += 12
    if p2 == "AM" and h2 == 12:
        h2 = 0

    # 返回 24 小时制时间格式
    return f"{h1:02}:{m1} to {h2:02}:{m2}"


if __name__ == "__main__":
    main()
