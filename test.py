import time
from selenium import webdriver
from bs4 import BeautifulSoup
import numpy as np
import csv

print(time.ctime(time.time()))

def write_csv(match):
    with open('csv_write_dictwriter.csv', 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
                f, fieldnames=list(match.keys()), quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(match)

def click_time (css_selector, k):
    elements = driver.find_elements_by_css_selector(css_selector)
    elements[k].click()

def htmlinner(css_selector):
    container = driver.find_element_by_css_selector(css_selector).get_attribute('innerHTML')
    soup = BeautifulSoup(container, 'html.parser')
    return soup

def second_otbor(match,id):
    matches.update({id: {'id': id}})
    league = driver.find_element_by_css_selector("span[class*='tournamentHeader__country']").text
    if league == "США: NCAA":
        return print('NCAA')
    matches[id].update({'лига': league})
    print(matches[id]['лига'])

    name_command = list(map(lambda x: x.text, match.select('div[class*="participant__participantName participant__overflow"]')))
    if name_command[0][-2:] == " W":
        name_command = [(i[:-2]+" (Ж)") for i in name_command]
    matches[id].update({'команды': name_command})
    print(matches[id]['команды'])

    try:
        score_q = [i.text for i in match.select('div[class*="smh__part smh__"]')]
        score_q = score_q[:5] + score_q[6:11]
        score_q = list(map(lambda x: int(x), score_q))
        matches[id].update({'общий счёт1': score_q[0]})
        matches[id].update({'общий счёт2': score_q[5]})
        matches[id].update(dict(zip(['q11', 'q12', 'q13', 'q14'], score_q[1:5])))
        matches[id].update(dict(zip(['q21', 'q22', 'q23', 'q24'], score_q[6:])))
    except:
        return print('нет счёта')

    click_time("a[href='#odds-comparison']", 0)
    if driver.find_elements_by_css_selector("a[href='#odds-comparison/home-away']") == [] \
            or driver.find_elements_by_css_selector("a[href='#odds-comparison/over-under']") == []:
        return print('нет коэффициента')
    if len(driver.find_elements_by_css_selector("div[class*='ui-table__row']")) != 0:
        container_match = htmlinner("div[class*='ui-table__row']")
        odd_command = [float(i.text.replace('-', '1')) for i in container_match.select('a[class*="oddsCell__odd"]')[:2]]
    else:
        odd_command = [0, 0]
    if len(odd_command) == 1:
        odd_command = [0, 0]
    print(odd_command)
    matches[id].update({'1х': odd_command[0], '2х': odd_command[1]})

    click_time("a[href='#odds-comparison/over-under']", 0)
    if driver.find_elements_by_css_selector("a[href='#odds-comparison/over-under/1st-qrt']") != []:
        click_time("a[href='#odds-comparison/over-under/1st-qrt']", 0)
        container_match = htmlinner("div[class*='oddsTab__tableWrapper']")
        tq = container_match.select('span[class*="oddsCell__noOddsCell"]')
        total_q = int(float(tq[len(tq) // 2].text))
    else:
        container_match = htmlinner("div[class*='oddsTab__tableWrapper']")
        tq = container_match.select('span[class*="oddsCell__noOddsCell"]')
        total_q = int(float(tq[len(tq) // 2].text)) // 4
    print(total_q)
    matches[id].update({'тотал': total_q})
    write_csv(matches[id])

driver = webdriver.Firefox()
driver.implicitly_wait(4)
driver.get('https://www.flashscore.ua/basketball/')
current_window = driver.current_window_handle
driver.execute_script("window.open('about:blank', 'tab2');")
# отркываем браузер, запоминаем уникальное имя вкладки, открываем вторую.

# click_time("div.searchWindowPromo__close", 0)
click_time("div.filters__tab", 3)
for g in range(1):
    matches = dict()
    click_time("div[class*='calendar__navigation']", 0)
    time.sleep(5)
# click_time("div.calendar__direction.calendar__direction--yesterday",0)
# time.sleep(5)

    container = driver.find_element_by_css_selector("div[id=live-table]").get_attribute('innerHTML')
    soup = BeautifulSoup(container, 'html.parser')
    matches_all = soup.select('.event__match.event__match--twoLine')

    for match in matches_all:
        if match.select_one('div.event__stage').text in ['Завершено']:
            driver.switch_to.window('tab2')
            url_match = 'https://www.flashscore.ua/match/{}/#match-summary'.format(match['id'][4:])
            driver.get(url_match)
            time.sleep(2)
            container_match = htmlinner("div[id=detail]")
            elements = driver.find_elements_by_css_selector("a[href='#odds-comparison']")
            if elements == []:
                driver.switch_to.window(current_window)
            else:
                second_otbor(container_match, match['id'])
                driver.switch_to.window(current_window)
driver.quit()
            # uslovie(match['id'])
            # print (matches[match['id']])
    # click_time ("div.calendar__direction.calendar__direction--yesterday", 0)
    # time.sleep(4)
