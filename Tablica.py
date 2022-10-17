import csv
import sqlite3
from sqlite3 import Error
from collections import Counter

def sql_connection():
    try:
        con = sqlite3.connect('data_stavka_basket.db')
        return con
    except Error:
        print(Error)

def sql_table(con):
    cursorObj = con.cursor()

with open('csv_write_dictwriter.csv', encoding = 'UTF-8') as f:
    reader = csv.DictReader(f, fieldnames=['id','лига','команды','общий счёт1','общий счёт2','q11',
                                           'q12','q13','q14','q21','q22','q23','q24'
                                            ,'1х','2х','тотал'])
    #con = sql_connection()
    #cursorObj = con.cursor()
    #rows = cursorObj.execute('SELECT league, id_match, isxod, stav FROM basket where id>1100 and strateg="4.71"').fetchall()
    # con.commit()
    # con.close()
    i=0
    j=0
    out_league_rate = []
    spic_row = []
    league_set = set()
    l_rate = []
    l_rate_league = []
    #for row in reader:
        #league = row['лига']
        #if league.find(' - ') != -1:
            #league = league[:league.find(' - ')]
        #row.update(лига=league)
        #spic_row.append(row)
        #league_set.add(league)

    #for league in league_set:
    for row in reader:
        #l_rate_league = []
        #kk = 0

            #if row['лига'] != league:
                #continue
            league = row['лига']
            #"""Обрезка лиг для более понятного анализа (убрали туры и прочее"""
            #if league.find(' - ') != -1:
            #    league = league[:league.find(' - ')]
            #if "пп" not in league: continue
            #if "(Ж)" in row['команды']: continue
            #if "США" in league: continue
            #if row_sq[1] != row['id']: continue
            q11, q12, q13, q14 = int(row['q11']), int(row['q12']), int(row['q13']), int(row['q14'])
            q21, q22, q23, q24 = int(row['q21']), int(row['q22']), int(row['q23']), int(row['q24'])
            total_sum1, total_sum2 = int(row['общий счёт1']), int(row['общий счёт2'])
            tot = int(row['тотал'])
            kx1, kx2 = float(row['1х']), float(row['2х'])
            total_q1 = q11+q21-tot
            total_q2 = q12+q22-tot
            total_q3 = q13+q23-tot
            total_q4 = q14+q24-tot
            #print(total_q1)
            total_q_sum = [total_q1, total_q2, total_q3, total_q4]
                #ТМ во второй четверти
                #and kx1<=kx2 and q11==q21 and kx1>1.55
            if min(kx1, kx2) == kx1 or kx1 == kx2:
                k = kx1
                k_and = kx2
                q1_vin, q1_and = q11, q21
                q2_vin, q2_and = q12, q22
                q3_vin, q3_and = q13, q23
                q4_vin, q4_and = q14, q24
            else:
                k = kx2
                k_and = kx1
                q1_vin, q1_and = q21, q11
                q2_vin, q2_and = q22, q12
                q3_vin, q3_and = q23, q13
                q4_vin, q4_and = q24, q14

            # print(sum(total_q_sum))

            if 5.0 <= k_and < 6.0:
                j += 1
                if q1_and +1.5 > q1_vin or q2_and+0.5 > q2_vin or q3_and+0.5 > q3_vin or q4_and+1.5 > q4_vin:
                    i += 1
                    if q1_and+1.5 > q1_vin:
                        q_rate = 1
                    elif q2_and+0.5 > q2_vin:
                        q_rate = 2
                    elif q3_and+0.5 > q3_vin:
                        q_rate = 3
                    elif q4_and+1.5 > q4_vin:
                        q_rate = 4
                    l_rate.append(q_rate)
                    l_rate_league.append(q_rate)
        #h_cnt = Counter(l_rate_league)
        #hh = '{}, {}, {}, {}, {}, Всего, {}'.format(league, h_cnt[1], h_cnt[2], h_cnt[3], h_cnt[4], kk)
        #print(hh)
        #out_league_rate.append(f'{hh}')
    print(Counter(l_rate))

            # if -4 <= q1_vin - q1_and <= 4 and 37 < total_q < 41 and total_q_sum[0] < 2 and not (0 < k <= 1.3 or 1.7 <= k < 1.8): #or (q1_vin<=q1_and and q2_vin>q2_and):
            #     continue
            # if k<1.3 and q1_vin>=q1_and-1 and total_q1<2:
            #     j += 1
            # #     # print ((q11+q12+q13+q14+q21+q22+q23+q24)%2)
            #     if q12 + q22 <= total_q:
            #         i += 1
# (q1_vin+q1_and)%2!=1 and (q2_vin+q2_and)%2!=1 and (q3_vin+q3_and)%2!=1

    print('Всего:', j, '\n', 'Плюсов:', i, '\n', 'Минусов:', j-i, '\n', 'Проходимость:', round(i*100/j, 3), '%')
#     cnt1 = Counter(l_rate)
#     cnt2 = Counter(l_rate_all)
    #with open('Стратегия v01 рейтинг по четвертям.txt', 'w') as h1:
        #[h1.write(f'{i}\n') for i in out_league_rate]
#     with open('Все лиги.txt', 'w') as h1, open('Лиги минуса.txt', 'w') as h2:
#         for key, value in cnt2.items():
#             h1.write(f'{key},{value}\n')
#         for key, value in cnt1.items():
#             h2.write(f'{key},{value}\n')

            #if-2<=q1_vin - q1_and<=7 and 37<total_q<44 and total_q_sum[0]<0:
            # if 0<=k<=1.2 or 1.75<=k<=110: continue
            # i+=1
            # j+=row_sq[2]
    #         if -3<=q1_vin - q1_and<=4 and 37<total_q<42 and total_q_sum[0]<1 and not (0<k<1.3 or 1.7<=k<1.8):
    #             if q2_vin+q2_and <= total_q+1:
    #                 i+=1
    #             else:
    #                 #print(total_q)
    #                 j+=1
    # print(i,j, i/(j+i))
# 4.71  if q1_vin-q2_vin<0 and q3_vin<q2_vin and 20>q1_vin+q2_vin+q3_vin-(q1_and+q2_and+q3_and)>10 and q1_vin-q1_and>=-1 and q2_vin-q2_and>=-1 and q3_vin-q3_and>=-1:
#2.3  if q2_vin+1>= q2_and: if q2_vin > (total_q//2)-2:
#2.4 if q2_vin+1 >= q2_and:
#3.8  0.1 0.81
# ТЕОРИЯ ДОГОНА БАСКЕТ
# if 1.6>=k>1.5 and total_q>41:
#                 j+=1
#                 if q1_and>q1_vin or q2_and>q2_vin or q3_and>q3_vin or q4_and>q4_vin:
