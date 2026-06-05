def main():
    tweet = input('Input: ')
    print(shorten(tweet))

def shorten(word):
    # 使用集合来提高查找效率
    vowels = set('aeiou')
    # 使用列表推导式来移除元音
    return ''.join([char for char in word if char not in vowels])

if __name__ == "__main__":
    main()
