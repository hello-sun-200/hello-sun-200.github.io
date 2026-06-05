def convert(sentence):
    return sentence.replace(':)', "🙂").replace(':(', "🙁")


def main():
    sentence = input()
    print(convert(sentence))


main()
