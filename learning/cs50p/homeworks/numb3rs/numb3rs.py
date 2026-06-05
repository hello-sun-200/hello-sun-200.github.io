import re
import sys

def main():
    print(validate(input("IPv4 Address: ")))


def validate(ip):
    # 正则表达式：匹配任意有效的数字段
    pattern = r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$"

    if match := re.search(pattern, ip):
        # 检查每个部分是否在 0-255 范围内，并且没有前导零（除了 "0"）
        for i in range(1, 5):
            part = match.group(i)
            # 如果该部分不是 "0"，且以 "0" 开头，则是无效的
            if (part != "0" and part.startswith("0")) or not (0 <= int(part) <= 255):
                return False
        return True
    else:
        return False


if __name__ == "__main__":
    main()
