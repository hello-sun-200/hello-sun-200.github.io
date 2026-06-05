def main():
    tweet=input('Input: ')
    print(shorten(tweet))


def shorten(word):
    words=[]
    for c in word:
        if c.lower() in 'aeiou':
            pass
        else:
            words.append(c)
    return "".join(words)



if __name__ == "__main__":
    main()

