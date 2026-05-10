import chardet

with open('data/kospi_code.csv', 'rb') as f:
    result = chardet.detect(f.read())
    print(result)
