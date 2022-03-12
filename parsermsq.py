import time
from selenium import webdriver
from bs4 import BeautifulSoup
import telebot
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from telebot import apihelper
import sqlite3
from sqlite3 import Error
import traceback
import re

def connect_bot_tele():
    # apihelper.proxy = {'https':'https://{}:{}'.format(ip, port)}
    return telebot.TeleBot('1065832827:AAFcavmKkyxiXHWPprEzPyJg72tloC8EzO8')

def sql_connection():
    try:
        con = sqlite3.connect('data_stavka_basket.db')
        return con
    except Error:
        print(Error)

def sql_table_save(con, index_stav, id, stav, znach_stav, strateg, id_sms):
    cursorObj = con.cursor()
    #cursorObj.execute("CREATE TABLE basket(id INTEGER PRIMARY KEY, id_match text, id_sms integer, league text, name_comand1 text, name_comand2 text, stav text, znach_stav integer, strateg real, match_stav text, isxod integer)")
    cursorObj.execute("""INSERT INTO basket(id ,id_match, id_sms, league, name_comand1, name_comand2, stav, znach_stav, strateg, match_stav)
                      VALUES(?,?,?,?,?,?,?,?,?,?)""",(index_stav, id, id_sms, matches[id]['лига'],
                      matches[id]['команды'][0], matches[id]['команды'][1], stav,
                      znach_stav, strateg, matches[id]['ставка']))
    con.commit()
    con.close()

def send_posts_text(stav= '',id= '',num_st= 'NULL', znach_stav= 'NULL'):
    if matches[id]['ставка'] == '':
        print('no text')
    else:
        con = sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute('SELECT * FROM basket')
        rows = cursorObj.fetchall()
        index_stav = len(rows)+1
        send = True
        while send:
            try:
                bot = connect_bot_tele()
                msg = '\n'.join(['#b{} {}'.format(index_stav, matches[id]['лига']), '\n{}'.format(matches[id]['стат_лига']), '\n{} - {}'.format(*matches[id]['команды']),'{} - я четверть'.format(matches[id]['четверть']),
                        '\n[{}] {}'.format(matches[id]['счёт1'], matches[id]['общий счёт1']), '[{}] {}'.format(matches[id]['счёт2'], matches[id]['общий счёт2']),
                        'Коэф-ы: П1 (*{}*) - П2 (*{}*)'.format(*matches[id]['1х2']),
                         'Нач. тотал четверти: *{}*'.format(matches[id]['тотал']),
                         '\n{}'.format(matches[id]['разница тотал']), 'СТАВКА: *{}*'.format(matches[id]['ставка'])])
                time.sleep(2)
                res = bot.send_message('-1001415140245', msg, timeout=20, parse_mode="Markdown")
                send = False
            except:
                print('NOnoNO proxi')
                send = True
                time.sleep(20)
        sql_table_save(con, index_stav, id, stav, znach_stav, num_st, res.message_id)

# def edit_sms_tel(isxod, id_mes, id, index_stav):
#     sml = {1:'✅',0:'❌'}
#     isxod = sml[isxod]
#     send = True
#     while send:
#         try:
#             bot = connect_bot_tele()
#             msg = '\n'.join(['#b{} {}'.format(index_stav, matches[id]['лига']), '\n{}'.format(matches[id]['стат_лига']), '\n{} - {}'.format(*matches[id]['команды']),'{} - я четверть'.format(matches[id]['четверть']),
#                         '\n[{}] {}'.format(matches[id]['счёт1'], matches[id]['общий счёт1']), '[{}] {}'.format(matches[id]['счёт2'], matches[id]['общий счёт2']),
#                         'Коэф-ы: П1 (*{}*) - П2 (*{}*)'.format(*matches[id]['1х2']),
#                          'Нач. тотал четверти: *{}*'.format(matches[id]['тотал']),
#                          '\n{}'.format(matches[id]['разница тотал']), 'СТАВКА: *{}*'.format(matches[id]['ставка'])])
#             time.sleep(2)
#             bot.edit_message_text(chat_id='-1001415140245', message_id=id_mes, text=msg, parse_mode="Markdown")
#             send = False
#             print('сообщение отредактировано')
#         except:
#             print('не удалось')
#             send = True
#             time.sleep(30)

def click_time(css_selector, k):
    try:
        elements = driver.find_elements_by_css_selector(css_selector)
        #elements[k].location_once_scrolled_into_view
        elements[k].click()
    except selenium.common.exceptions.ElementNotInteractableException:
        click_time(css_selector, k)
        # обрабатываем клик по селектору

def first_choice(match, id):
    try:
        set_quart = match.select_one('div.event__stage--block').text
        # print(set_quart)
    except:
        return False
    con = sql_connection()
    cursorObj = con.cursor()
    if set_quart in ['Завершено', 'Після овертайму'] or set_quart[0] == 'О' or (set_quart == 'Перерва' and len(match.select('event__part')) >= 8):
        cursorObj.execute('SELECT id, stav, znach_stav, strateg, id_sms, match_stav FROM basket WHERE id_match = "{}" AND isxod IS NULL'.format(id))
        rows = cursorObj.fetchall()
        for row in rows:
            q = int(row[3][0])
            h = match.select('div.event__part.event__part--home.highlighted.event__part--{}'.format(q))
            if h == []: h = match.select('div.event__part.event__part--home.event__part--{}'.format(q))
            a = match.select('div.event__part.event__part--away.highlighted.event__part--{}'.format(q))
            if a == []: a = match.select('div.event__part.event__part--away.event__part--{}'.format(q))
            a, h = a[0].text, h[0].text
            try:
                kx1, kx2 = matches[id]['1х2'][0], matches[id]['1х2'][1]
            except:
                print('В словаре нет данных о матче {}'.format(row[0]))
                return False
            if row[3] in ['3.8', '3.9', '4.1', '3.81']: #row[3] == '3.8' or row[3] == '3.9' or row[3] == '4.1' or row[3] == '3.81'
                h = match.select('div.event__score.event__score--home.highlighted')
                if h == []: h = match.select('div.event__score.event__score--home')
                a = match.select('div.event__score.event__score--away.highlighted')
                if a == []: a = match.select('div.event__score.event__score--away')
                a, h = a[0].text, h[0].text
                if row[1] == 'ТМ':
                    if int(h)+int(a) < row[2]:
                        isxod = 1
                    else:
                        isxod = 0
                elif row[1] == 'ТБ':
                    if int(h)+int(a) > row[2]:
                        isxod = 1
                    else:
                        isxod = 0
                elif row[1] == 'ЧН':
                    if (int(h)+int(a)) % 2 == 1:
                        isxod = 1
                    else:
                        isxod = 0
            elif row[3] == '4.7':
                if kx1 < kx2:
                    if int(h) > (int(matches[id]['тотал'])//2)-2:
                        isxod = 1
                    else:
                        isxod = 0
                elif kx1 > kx2:
                    if int(a) > (int(matches[id]['тотал'])//2)-2:
                        isxod = 1
                    else:
                        isxod = 0
            elif row[3] == '2.31':
                if kx1 < kx2:
                    if int(h)+2 > int(a):
                        isxod = 1
                    else:
                        isxod = 0
                elif kx1 > kx2:
                    if int(a)+2 > int(h):
                        isxod = 1
                    else:
                        isxod = 0
            elif row[3] == '2.33':
                if kx1 < kx2:
                    if int(h) > int(a):
                        isxod = 1
                    else:
                        isxod = 0
                elif kx1 > kx2:
                    if int(a) > int(h):
                        isxod = 1
                    else:
                        isxod = 0
            elif row[3] == '4.71':
                if kx1 < kx2:
                    sqrf = int(h)
                    sqra = int(a)
                else:
                    sqrf = int(a)
                    sqra = int(h)
                if sqra+2 > sqrf:
                    isxod = 1
                else:
                    isxod = 0
            elif row[3] == '2.32':
                if kx1 < kx2:
                    sqrf = int(h)
                    sqra = int(a)
                else:
                    sqrf = int(a)
                    sqra = int(h)
                if sqra+2.5 > sqrf:
                    isxod = 1
                else:
                    isxod = 0
            elif row[1] == 'ТМ':
                tot_del = int(h)+int(a)-row[2]
                if tot_del <= 0:
                    isxod = 1
                else:
                    isxod = 0
            else:
                tot_del = int(h)+int(a)-row[2]
                if tot_del > 0:
                    isxod = 1
                else:
                    isxod = 0
            cursorObj.execute('UPDATE basket SET isxod = {} where id = {}'.format(isxod, row[0]))
            print('обновлено')
            # con.commit()
            # edit_sms_tel(isxod, row[4], id, row[0])
            # print('отредактировано')
        con.commit()
        con.close()
        if match['id'] in matches:
            del matches[id]
            print('удален' + match['id'])
        return False
    if set_quart in ['Завершено', "Задержка", 'Після овертайму'] or set_quart[0] == 'О':
        if match['id'] in matches:
            del matches[id]
            print('удален просто' + match['id'])
        return False
    elif set_quart == 'Перерва' and len(match.select('event__part')) >= 8:
        if match['id'] in matches:
            del matches[id]
            print('удален просто' + match['id'])
        return False
    if set_quart != 'Перерва':
        try:
            quart = int(set_quart[0])
        except:
            return False
        if set_quart[-3:].strip() != 'рть':
            min_q = int(set_quart[-3:-1].strip())
        else:
            min_q = 0
    else:
        quart = 3
        min_q = 0
    if match['id'] in matches:
        if matches[id]['четверть'] == quart:
            return False
    if quart != 1 and min_q not in {9, 10, 11, 12}:
        matches.update({id: {'четверть': quart}})
        return True
    else:
        return False

def second_otbor(match,id):
    league = driver.find_element_by_css_selector("span[class*='tournamentHeader__country']").text
    matches[id].update({'лига': league})
    print(matches[id]['лига'])

    name_command = list(map(lambda x: x.text, match.select('div[class*="participant__participantName participant__overflow"]')))
    if name_command[0][-2:] == " W":
        name_command = [(i[:-2]+" (Ж)") for i in name_command]
    matches[id].update({'команды': name_command})
    print(matches[id]['команды'])

    print(matches[id]['четверть'])
    score_q = [i.text for i in match.select('div[class*="smh__part smh__"]')]
    score_q = score_q[:matches[id]['четверть']] + score_q[6:matches[id]['четверть']+6]
    score_q = list(map(lambda x: int(x), score_q))
    print(score_q)
    matches[id].update({'общий счёт1': score_q[0]})
    matches[id].update({'общий счёт2': score_q[matches[id]['четверть']]})
    matches[id].update({'счёт1': score_q[1:matches[id]['четверть']]})
    matches[id].update({'счёт2': score_q[matches[id]['четверть']+1:]})
    print(matches[id]['счёт1'], matches[id]['общий счёт1'])
    print(matches[id]['счёт2'], matches[id]['общий счёт2'])

    click_time("a[href='#odds-comparison']", 0)
    if driver.find_elements_by_css_selector("a[href*='#odds-comparison/home-away']") == [] \
            or driver.find_elements_by_css_selector("a[href*='#odds-comparison/over-under']") == []:
        return False
    if len(driver.find_elements_by_css_selector("div[class*='ui-table__row']")) != 0:
        container_match = htmlinner("div[class*='ui-table__row']")
        odd_command = [float(i.text.replace('-', '1')) for i in container_match.select('a[class*="oddsCell__odd"]')[:2]]
    else:
        odd_command = [0, 0]
    if len(odd_command) == 1:
        odd_command = [0, 0]
    matches[id].update({'1х2': odd_command})
    print(matches[id]['1х2'])

    click_time("a[href*='#odds-comparison/over-under']", 0)

    if driver.find_elements_by_css_selector("a[href*='#odds-comparison/over-under/1st-qrt']") != []:
        click_time("a[href='#odds-comparison/over-under/1st-qrt']", 0)
        container_match = htmlinner("div[class*='oddsTab__tableWrapper']")
        tq = container_match.select('span[class*="oddsCell__noOddsCell"]')
        total_q = int(float(tq[len(tq) // 2].text))
        print('посчиталось', total_q)
    else:
        container_match = htmlinner("div[class*='oddsTab__tableWrapper']")
        tq = container_match.select('span[class*="oddsCell__noOddsCell"]')
        total_q = int(float(tq[len(tq) // 2].text)) // 4
        print('посчиталось', total_q)
    matches[id].update({'тотал': total_q})
    print(matches[id]['тотал'])

def uslovie(id, stav='', tot_stav='NULL', num_st=None):
    if num_st is None:
        num_st = []
    total_q_sum = list(map(lambda a, b: a + b - matches[id]['тотал'], matches[id]['счёт1'], matches[id]['счёт2']))
    matches[id].update({'разница тотал': total_q_sum})
    q = matches[id]['четверть']
    kx1, kx2 = matches[id]['1х2'][0], matches[id]['1х2'][1]
    q11, q21 = matches[id]['счёт1'][0], matches[id]['счёт2'][0]
    tot = matches[id]['тотал']
    koridor = ''
    print(total_q_sum)
    spec_stav = '{}-й четверти'.format(q)
    if min(kx1, kx2) == kx1:
        k = kx1
        n_it, n_co = 1, 2
    else:
        k = kx2
        n_it, n_co = 2, 1

    if q == 2:
        if min(kx1, kx2) == kx1:
            q1_vin, q1_and = q11, q21
        else:
            q1_vin, q1_and = q21, q11

        if 1 <= q1_vin - q1_and <= 6 and 39 < tot < 41 and total_q_sum[0] < 12 and not \
                ((0 < k <= 1.09) or (1.53 <= k < 2) or (1.38 < k < 1.46)):
            num_st, tot_stav = 2.2, tot+1
            stav = 'ТМ'
            koridor = 'Коридор {}-{}'.format(tot-11, tot+8)
            # Проходимость 68.098 %, мин кэф: 1,5. 330 матчей. 31.01.2022

        elif total_q_sum[0] <= -8 and q1_vin - q1_and <= 2 and k <= 1.61 and tot < 42:
            num_st, tot_stav = 2.3, tot+1
            stav = 'ТМ'
            koridor = 'Коридор {}-{}'.format(tot-10, tot+10)
            # Проходимость 70.164 %, мин кэф: 1,5. 610 матчей. 31.01.2022

        elif total_q_sum[0] >= -7 and total_q_sum[0] < 5 and q1_vin >= q1_and and tot > 44:
            num_st, tot_stav = 2.7, tot+1
            stav = 'ТМ'
            koridor = 'Коридор {}-{}'.format(tot-11, tot+9)
            # Проходимость 69.421 %, мин кэф: 1,5. 242 матчей. 31.01.2022

        elif q1_vin > q1_and and q1_vin - q1_and > 9 and total_q_sum[0] < 2 and k > 1.44 and tot < 40:
            num_st, tot_stav = 2.13, tot-2
            stav = 'ТБ'
            koridor = 'Коридор {}-{}'.format(tot-9, tot+9)
            # Проходимость 64.205 %, мин кэф: 1,6. 176 матчей. 31.01.2022

        elif q1_vin < q1_and and total_q_sum[0] > 2 and k > 1.44 and tot < 38:
            num_st, tot_stav = 2.14, tot - 2
            stav = 'ТБ'
            koridor = 'Коридор {}-{}'.format(tot - 8, tot + 9)
            # Проходимость 66.376 %, мин кэф: 1,6. 229 матчей. 31.01.2022

        print(stavka_gener(stav, str(num_st), tot_stav, spec_stav, id, koridor))
        stav = ""

        if total_q_sum[0] <= -1 and q1_vin - q1_and <= 2 and k <= 1.5 and tot < 55:
            num_st, tot_stav = 2.31, 1.5
            stav = 'Ф{}'.format(n_it)
            koridor = 'Коридор Ффав{}-Фанд{}'.format(6.5, 11.5)
            # Проходимость 72.507 %, мин кэф: 1,4. 2477 матчей. 31.01.2022

        if total_q_sum[0] <= 4 and q1_vin - q1_and <= 2 and k <= 1.13 and tot < 58:
            num_st, tot_stav = 2.33, 0
            stav = 'Ф{}'.format(n_it)
            koridor = 'Коридор Ффав{}-Фанд{}'.format(6.5, 11.5)
            # Проходимость 68.911 %, мин кэф: 1,5. 1084 матчей. 31.01.2022

        if (q1_vin > q1_and > q1_vin-5 or q1_vin-7 > q1_and > q1_vin-100) and k > 1.5:
            num_st, tot_stav = 2.32, 2.5
            stav = 'Ф{}'.format(n_co)
            koridor = 'Коридор Ффав{}-Фанд{}'.format(10.5, 9.5)

    elif q == 3:
        q12, q22 = matches[id]['счёт1'][1], matches[id]['счёт2'][1]
        if min(kx1, kx2) == kx1:
            q1_vin, q1_and = q11, q21
            q2_vin, q2_and = q12, q22
        else:
            q1_vin, q1_and = q21, q11
            q2_vin, q2_and = q22, q12

        if total_q_sum[0] - 2 < total_q_sum[1] and q1_vin > q1_and and q2_vin < q2_and and 13 > q1_vin + q2_vin - q1_and - q2_and > 2:
            num_st, tot_stav = 3.3, tot+1
            stav = 'ТМ'
            koridor = 'Коридор {}-{}'.format(tot-12, tot+6)
        elif total_q_sum[0] >= -30 and total_q_sum[1] >= 0 and sum(total_q_sum) >= 0 and k >= 0 and tot >= 40:
            print('к')
        elif total_q_sum[0] >= -12 and total_q_sum[0] <= 10 and total_q_sum[1] > total_q_sum[0] and k <= 1.7 and tot > 39:
            num_st, tot_stav = 3.5, tot+1
            stav = 'ТМ'
        elif abs(total_q_sum[1] - total_q_sum[0])> 6 and total_q_sum[1] < total_q_sum[0] and total_q_sum[1] <= -6 and total_q_sum[0] <= 5 and tot > 39:
            num_st, tot_stav = 3.7, tot+1
            stav = 'ТМ'
        print(stavka_gener(stav, str(num_st), tot_stav, spec_stav, id, koridor))

        stav=""
        if total_q_sum[0] == total_q_sum[1] and total_q_sum[0] < -3:
            num_st, tot_stav = 3.2, tot+1
            stav = 'ТМ'
            koridor = 'Коридор {}-{}'.format(tot-12, tot+7)
        elif total_q_sum[0] >= -20 and total_q_sum[1] >= -20 and sum(total_q_sum) > -5 and k >= 1.58 and tot > 41:#
            num_st, tot_stav = 3.4, tot-1
            stav = 'ТБ'
            koridor = 'Коридор {}-{}'.format(tot-6, tot+12)
        elif total_q_sum[0] <= 10 and total_q_sum[1] <= 0 and total_q_sum[0]+total_q_sum[1] <= -9 and k >= 1.5 and tot >= 40:#
            num_st, tot_stav = 3.6, tot+1
            stav = 'ТМ'
            koridor = 'Коридор {}-{}'.format(tot-12, tot+6)
        print(stavka_gener(stav, str(num_st), tot_stav, spec_stav, id, koridor))

        stav=""
        if total_q_sum[1]+total_q_sum[0] < -tot*4*0.093:
            num_st, tot_stav = 3.8, round(tot*4*0.832, 1)
            stav = 'ТБ'
            koridor = 'Коридор {}-{}'.format(round(tot*4*0.79, 1), round(tot*4*0.957, 1))
        elif total_q_sum[1]+total_q_sum[0] > tot*4*0.1:
            num_st, tot_stav = 3.9, round(tot*4*1.175, 1)
            stav = 'ТМ'
            koridor = 'Коридор {}-{}'.format(round(tot*4*1.07, 1), round(tot*4*1.25, 1))
        spec_stav = 'матче'
        if total_q_sum[1]+total_q_sum[0] < -tot*4*0.093 and ((q1_vin >= q2_vin and q2_vin <= q2_and) and (q1_vin > q1_and and q1_and <= q2_and)) and total_q_sum[0] > -12:
            num_st, tot_stav = 3.81, round(tot*4*0.849, 1)
            stav = 'ТБ'
            koridor = 'Коридор {}-{}'.format(round(tot*4*0.795, 1), round(tot*4*0.975, 1))
            # Проходимость 70,39%, мин кэф: 1,5. процент от всех матчей 13,63%. 31.01.2022

    elif q == 4:
        q12, q22 = matches[id]['счёт1'][1], matches[id]['счёт2'][1]
        q13, q23 = matches[id]['счёт1'][2], matches[id]['счёт2'][2]
        if min(kx1, kx2) == kx1:
            q1_vin, q1_and = q11, q21
            q2_vin, q2_and = q12, q22
            q3_vin, q3_and = q13, q23
        else:
            q1_vin, q1_and = q21, q11
            q2_vin, q2_and = q22, q12
            q3_vin, q3_and = q23, q13

        if total_q_sum[0] > -6 and total_q_sum[1] >= 3 and total_q_sum[2] > total_q_sum[1] and 1.8 > k > 1.13:#04.06 Проходимость: 0.6586
            num_st, tot_stav = 4.2, tot-1
            stav = 'ТБ'
            koridor = 'Коридор {}-{}'.format(tot-7, tot+11)
        elif max(total_q_sum) >= -3 and 24>abs(sum(total_q_sum)) >= 12 and q1_vin>q1_and and q2_vin <= q2_and and q3_vin < q3_and:
            num_st, tot_stav = 4.8, tot-1
            stav = 'ТБ'
            koridor = 'Коридор {}-{}'.format(tot-8,tot+10)
        elif q1_vin<=q2_vin<q3_vin and q1_vin+q2_vin+q3_vin-q1_and-q2_and-q3_and>2 and 1.5>k>1.26 and abs(total_q_sum[2]-total_q_sum[1])<8:#
            num_st, tot_stav = 4.3, tot-1
            stav = 'ТБ'
            koridor = 'Коридор {}-{}'.format(tot-7,tot+12)
        elif total_q_sum[2] - total_q_sum[1]>2 and 50>tot>39 and q1_and>=q1_vin and q2_and>q2_vin:#
            num_st, tot_stav = 4.4,tot+1
            stav = 'ТМ'
            koridor = 'Коридор {}-{}'.format(tot-8,tot+7)
        elif total_q_sum[2] - total_q_sum[1]>-3 and tot>43:#
            num_st, tot_stav = 4.5, tot+1
            stav = 'ТМ'
            koridor = 'Коридор {}-{}'.format(tot-12,tot+9)
        elif total_q_sum[2] >=-5 and total_q_sum[1]>=-5 and total_q_sum[2]<total_q_sum[0] and k<1.69 and q1_vin+q2_vin+q3_vin-q1_and-q2_and-q3_and>2:
            num_st, tot_stav = 4.6, tot+2
            stav = 'ТМ'
            koridor = 'Коридор {}-{}'.format(tot-10,tot+9)
        elif abs(total_q_sum[2] - total_q_sum[1])>= 2 and abs(sum(total_q_sum))>=9:
            if total_q_sum[2] > total_q_sum[1] and total_q_sum[2] >= 10 and sum(total_q_sum) >= 9:
                num_st,tot_stav = 4.11, tot-1
                stav = 'ТБ'
                koridor = 'Коридор {}-{}'.format(tot-6,tot+13)
            elif sum(total_q_sum) < 0 and 44>tot>33 and k<1.2:
                num_st,tot_stav = 4.12, tot+1
                stav = 'ТМ'
                koridor = 'Коридор {}-{}'.format(tot-11,tot+8)
        print(stavka_gener(stav, str(num_st), tot_stav, spec_stav, id, koridor))
        stav=""

        # if (q1_vin+q1_and)%2!=1 and (q2_vin+q2_and)%2!=1 and (q3_vin+q3_and)%2==1 and tot in [46,56,57,42,40,35]:
        #     num_st, tot_stav = 4.1, 'Чет'
        #     stav = 'ЧН'
        # в четверти
        # if (q1_vin+q1_and)%2!=1 and (q2_vin+q2_and)%2!=1 and (q3_vin+q3_and)%2!=1 and (total_q>46 or total_q in [43,38]):
        #     num_st, tot_stav = 4.1, 'Нечет'
        #     stav = 'ЧН'
        # в матче
        if (q1_vin % 2 == 0 and q2_vin % 2 == 0 and q2_vin % 2 == 0) and (q1_and % 2 != 1 or q2_and % 2 != 1 or q3_and%2!=1) and q1_vin>q1_and and q2_vin>=q2_and and q3_vin>=q3_and:
            num_st, tot_stav = 4.1, 'Нечет'
            stav = 'ЧН'
            spec_stav = 'матче'
            print(stavka_gener(stav, str(num_st), tot_stav, spec_stav, id, koridor))
            stav=""

        if q1_vin-q2_vin < -1 and q3_vin < q2_vin:
            num_st, tot_stav = 4.7, (tot//2)-2
            stav = 'ИТБ{}'.format(n_it)
            koridor = 'Коридор {}-{}'.format((tot//2)-5, (tot//2)+7)
            print(stavka_gener(stav, str(num_st), tot_stav, spec_stav, id, koridor))
            stav=""
        if q1_vin-q2_vin < 0 and q3_vin < q2_vin and q1_vin-q1_and >= -1 and q2_vin-q2_and >= -1 and q3_vin-q3_and>=-1:#
            num_st, tot_stav = 4.71, 1.5
            stav = 'Ф{}'.format(n_co)
            koridor = 'Можно рассмотреть фору +2.5 на фаварита'
    print(stavka_gener(stav, str(num_st), tot_stav, spec_stav, id, koridor))


def stavka_gener(stav, strateg, tot_stav, q, id, koridor):
    if stav == '':
        return 'нет ставки'
    con = sql_connection()
    cursorObj = con.cursor()
    j = cursorObj.execute('SELECT id FROM basket where isxod IS NULL').fetchall()
    if j == []:
        j = len(cursorObj.execute('SELECT id FROM basket').fetchall())
    else:
        j = j[0][0]
    rows = cursorObj.execute('SELECT isxod,league FROM basket where strateg={} and id>10000 and id<{}'.format(strateg, j)).fetchall()
    leag = matches[id]['лига'][0:matches[id]['лига'].find('-')]
    if len(rows) != 0:
        vin, all_st = 0, 0
        for row in rows:
            if row[1] == "США: НБА":
                continue
            all_st += 1
            vin += row[0]
        try:
            proxod = round(vin*100/all_st, 2)
        except:
            proxod = 0
        if proxod > 60:
            emoji_strat = '✳'
        elif proxod < 35 and proxod != 0:
            emoji_strat = '🔃'
        else:
            emoji_strat = '⚠'
    else:
        proxod = '❔'
        emoji_strat = ''
    if len(rows) != 0:
        vin, all_st = 0, 0
        for row in rows:
            if leag in row[1]:
                all_st += 1
                vin += row[0]
        try:
            proxod_l = round(vin*100/all_st, 2)
        except:
            proxod_l = 0
        if proxod_l > 55:
            emoji_l = '✳'
        else:
            emoji_l = '⚠'
    else:
        proxod_l = '❔'
        emoji_l = ''
    matches[id].update({'стат_лига': 'Статистика по лиге:\n{}% {}'.format(proxod_l, emoji_l)})
    stavka = '{} {} в {} {}{}[{}%]\n {}'.format(stav, tot_stav, q, emoji_strat, strateg, proxod, koridor)
    print(stavka)
    matches[id].update({'ставка': stavka})
    con.commit()
    con.close()
    send_posts_text(stav, id, strateg, tot_stav)
    return 'отрпавлено'

def track_matches(container):
    soup = BeautifulSoup(container, 'html.parser')
    matches_all = soup.select('div.event__match')
    for match in matches_all:
        if driver.find_elements_by_css_selector("div[id={}]".format(match['id'])) == []:
            continue
        if first_choice(match, match['id']):
            driver.switch_to.window('tab2')
            url_match = 'https://www.flashscore.ua/match/{}/#match-summary'.format(match['id'][4:])
            driver.get(url_match)
            time.sleep(2)
            container_match = htmlinner("div[id=detail]")
            elements = driver.find_elements_by_css_selector("a[href='#odds-comparison']")
            if elements == []:
                driver.switch_to.window(current_window)
            else:
                try:
                    if second_otbor(container_match, match['id']):
                        continue
                    print('первый отбор')
                    if '(Ж)' in matches[match['id']]['команды'][0]:
                        driver.switch_to.window(current_window)
                        continue
                    uslovie(match['id'])
                    print('условие')
                    driver.switch_to.window(current_window)
                except:
                    print('не удалось достать данные')
                    driver.switch_to.window(current_window)
                    print('============================')
        # url = 'https://www.myscore.ru/match/{}/#match-summary'.format(id_match)

def htmlinner (css_selector):
    box = driver.find_elements_by_css_selector(css_selector)
    if box != []:
        soup = BeautifulSoup(box[0].get_attribute('innerHTML'), 'html.parser')
        return soup
    return []
# Находим нужный блок HTML, преобразуем в объект супа

# opts = Options()
# opts.headless = True
profile = webdriver.FirefoxProfile()
profile.set_preference("media.volume_scale", "0.0")
# driver = webdriver.Firefox(options=opts, firefox_profile=profile)
driver = webdriver.Firefox(firefox_profile=profile)
# driver = webdriver.Firefox(options=opts)
# driver = webdriver.Firefox()
driver.implicitly_wait(4)

driver.get('https://www.flashscore.ua/basketball/')
current_window = driver.current_window_handle
driver.execute_script("window.open('about:blank', 'tab2');")
# отркываем браузер, запоминаем уникальное имя вкладки, открываем вторую.
# click_time("div.searchWindowPromo__close", 0)
# закрываем всплывающее промо
click_time("div.filters__tab", 1)
matches = dict()
temp_hash = 0
print('Запущенно')
# now = datetime.datetime(2020, 2, 16, 12, 00, 00)

while True:
# if (datetime.datetime.now()-now).days>=1:
#     print('сработал код')
#     now = now + datetime.timedelta(days=1)
    container = driver.find_element_by_css_selector("div[id=live-table]").get_attribute('innerHTML')
    time.sleep(1)
    if temp_hash != hash(container):
        track_matches(container)
        time.sleep(1)
        temp_hash = hash(container)

