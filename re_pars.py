import json
from cgitb import html
import requests
from datetime import datetime


headers = {"x-fsign": "SW9D1eZo"}


def main():
    feed = 'f_3_0_3_ru_1'
    url = f'https://d.soccerstand.com/ru/x/feed/{feed}'
    response = requests.get(url=url, headers=headers)
    data = response.text.split('¬')

    #print(data[1:500])

    data_list = {}

    for item in data[0:1000]:   # BX - минута четверти
        print (item)
        key, value = item.split('÷')
        if '~ZA' == key:
            league = value
            continue
        elif key == '~AA':
            id_match = value
            data_list.update({value: {}})
            data_list[id_match].update({'LG': league})
        elif key == 'AD': # AD - время начала матча, изначально в секундах и str
            date = str(datetime.fromtimestamp(int(value))) # value = str, переводим секунды с начала эпохи в целое число, fromtimestamp преобразует в дату/время, сохраняем в виде строки (для JSON)
            data_list[id_match].update({'AD': date})
        elif key == 'BX':
            data_list[id_match].update({'BX': value})

        #elif 
 
        
        #key = item.split('÷')[0]
        #value = item.split('÷')[-1]
        #if '~' in key:
            #data_list.append({key: value})
        #else:
            #data_list[-1].update({key: value})

    #print('ДАТА {}'.format(data_list[0].get('AD')))
    #print(json.dumps(data_list, ensure_ascii=False, indent=2))

    #for game in data_list:
        #if 'AA' in list(game.keys())[0]:
            #date = datetime.fromtimestamp(int(game.get("AD")))
            #team_1 = game.get("AE")
            #team_2 = game.get("AF")
            #score = f'{game.get("AG")} : {game.get("AH")}'

            #print(date, team_1, team_2, score, sep='/')

            # print(json.dumps(game, ensure_ascii=False, indent=2))



if __name__ == '__main__':
    main()
