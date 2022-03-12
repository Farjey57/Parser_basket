import requests

with open(r'C:\Users\Сергей\Downloads\dataset_24476_3.txt') as f:
    for number in f:
        url = 'http://numbersapi.com/{}/math?json=true'.format(number.rstrip())
        res = requests.get(url, timeout=5)
        # print(res.status_code)
        # print(res.headers['Content-Type'])
        if res.json()['found']:
            print('Interesting')
        else:
            print('Boring')
# Считываем построчно числа, подставляем с убраным переносом,
# отправляем GET получаем ответ в json, ищем тег 'found'(True or False)
# печатаем ответ