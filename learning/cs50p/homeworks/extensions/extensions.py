name = input("File name: ").strip().lower().split('.')
match name[-1]:
    case 'txt':
        print('text/plain')
    case  'gif' | 'png':
        print('image/'+name[-1])
    case 'jpeg' | 'jpg':
        print('image/jpeg')
    case 'pdf' | 'zip':
        print('application/'+name[-1])
    case _:
        print("application/octet-stream")
