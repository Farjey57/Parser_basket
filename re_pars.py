import json
from cgitb import html
import requests
from datetime import datetime


headers = {"x-fsign": "SW9D1eZo"}


def main():
    feed = 'f_3_0_3_ru_1'
    url = f'https://50.flashscore.ninja/60/x/feed/{feed}'
    response = requests.get(url=url, headers=headers)
    data = response.text.split('¬')

    feed_live = 'r_3_1'
    url_live = f'https://50.flashscore.ninja/60/x/feed/{feed_live}'
    response_live = requests.get(url=url_live, headers=headers)
    data_live = response_live.text.split('¬')

    url_odds = 'https://50.flashscore.ninja/60/x/feed/df_od_1_hYJL8jRi'
    response_odds = requests.get(url=url_odds, headers=headers)
    data_odds = response_odds.text.split('¬')

    # print(data_live[1:])
    # print(data_odds[1:])

    data_list = {}

    for item in data[1:-1]:
        print (item)
        key, value = item.split('÷')
        if '~ZA' == key: # ZA - маркер лиги, запоминаем для следующих впереди матчей
            league = value
            continue
        elif key == '~AA': # AD - маркер матча
            id_match = value
            data_list.update({value: {}})
            data_list[id_match].update({'LG': league})
            data_list[id_match].update({'AO': 'не начался/перенос'})
            continue
        elif key == 'AD': # AD - время начала матча, изначально в секундах и str
            date = str(datetime.fromtimestamp(int(value))) # value = str, переводим секунды с начала эпохи в целое число, fromtimestamp преобразует в дату/время, сохраняем в виде строки (для JSON)
            data_list[id_match].update({key: date})
            continue
        elif key == 'AX':  # AX - 0 - не начался или тех.поражение 1 - начался или завершился
            value = 'начался/завершился' if int(value) else "не начался/тех.п./перенос"
            data_list[id_match].update({'AX': value})
            continue
        elif key == 'AB':  # AB - 1 - не начался 2 - идет сейчас 3 - завершен
            value = ['Не начался', 'лайв', 'завершен/тех.п./перенесен'][int(value)-1]
            data_list[id_match].update({'AB': value})
            continue
        elif key == 'AO':  # AO - время после начала. Нет только у не начавшихся и перенесенных.
            data_list[id_match].update({'AO': value})
            continue
        elif key in ('BX', 'AE', 'AG', 'BA', 'BC', 'BE', 'BG', 'BI', 'AF', 'AH',
                    'BB', 'BD', 'BF', 'BH', 'BJ', 'AI'):
            data_list[id_match].update({key: value})
    
    for item in data_live[1:-1]:
        key, value = item.split('÷')
        if key == '~AA': # AD - маркер матча
            id_match = value
        elif key in ('BX', 'AE', 'AG', 'BA', 'BC', 'BE', 'BG', 'BI', 'AF', 'AH',
                    'BB', 'BD', 'BF', 'BH', 'BJ'):
            if id_match in data_list:
                data_list[id_match].update({key: value})
                data_list[id_match].update({'LIVE': 'live'})
            else:
                print(f"Ключ {id_match} отсутствует в словаре")
        #AE, AF - названия команд хозяева/гости
        #BX - минута четверти либо маркер перерыва/окончания/не начала/переноса
        #AG - Общий счет команды дома
        #BA, BС, BE, BG, BI - 1-4 четверть, овертайм команда дома
        #AH - Общий счет команды гость
        #BB, BD, BF, BH, BJ - 1-4 четверть, овертайм команда гость
        #AI - маркер лайва 
    
    # for item in data_odds[1:200]:
    #     print(item)

    # print('ДАТА {}'.format(data_list[0].get('AD')))
    print(json.dumps(data_list, ensure_ascii=False, indent=2))

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
