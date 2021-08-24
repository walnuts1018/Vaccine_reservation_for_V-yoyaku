from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from socket import socket, AF_INET, SOCK_DGRAM
from struct import unpack
from datetime import date, datetime
import calendar

CHROMEDRIVER = "/usr/bin/chromedriver"
 
def get_driver(init_flg):
     
    #　ヘッドレスモードでブラウザを起動
    options = Options()
    options.add_argument('--headless')
 
 
    # ブラウザーを起動
    driver = webdriver.Chrome(CHROMEDRIVER, options=options)
     
    return driver


def ntp_now(server, port = 123):

    with socket(AF_INET, SOCK_DGRAM) as s:
        s.sendto(b'\x1b' + 47 * b'\0', (server, port))
        result = s.recvfrom(1024)[0]
    if result:
        return datetime.fromtimestamp(unpack(b'!12I', result)[10] - 2208988800)
    else:
        None


if __name__ == '__main__':
     
    url = "https://v-yoyaku.jp/341002-hiroshima"
     
    #　ヘッドレスモードでブラウザを起動
    options = Options()
    #options.add_argument('--headless')
 
    # ブラウザーを起動
    driver = webdriver.Chrome(CHROMEDRIVER, options=options)
     
    # urlにアクセス
    driver.get(url)

    #接種券番号、パスワードを入力
    f = open('config.json','r')
    j=json.load(f)
    ticket_number=j["ID"]["number"]
    password=j["ID"]["pass"]
    f.close()
    print("login情報取得完了")

    element = WebDriverWait(driver, 10).until(
    expected_conditions.presence_of_element_located((By.ID, "login_id"))
    )

    driver.execute_script("window.scrollTo(0,2900);")
    time.sleep(1)
    #driver.find_element(By.ID, "login_id").click()
    driver.find_element_by_xpath("//*[@id='login_id']").send_keys(ticket_number)
    #driver.find_element(By.ID, "login_pwd").click()
    driver.find_element(By.ID, "login_pwd").send_keys("1018")
    print("入力完了")
    driver.find_element_by_xpath("//*[@id='btn_login']").click()
    print("ログイン完了")

    element = WebDriverWait(driver, 10).until(
    expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#mypage_accept font"))
    )

    #予約・変更するボタン
    driver.find_element(By.CSS_SELECTOR, "#mypage_accept font").click()
    print("予約ページ遷移完了")

    element = WebDriverWait(driver, 10).until(
    expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#btn_Search_Medical > font"))
    )

    driver.execute_script("window.scrollTo(0,870);")
    #接種会場を選択ボタン
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, "#btn_Search_Medical > font").click()
    print("接種会場ページ遷移完了")
    time.sleep(1)
    element = WebDriverWait(driver, 10).until(
    expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#btn_Search_Medical > font"))
    )

    #検索ボタン
    driver.find_element(By.ID, "btn_search_medical").click()

    #多分検索処理？
    element = driver.find_element(By.ID, "btn_search_medical")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    element = driver.find_element(By.CSS_SELECTOR, "body")
    actions = ActionChains(driver)
    driver.execute_script("window.scrollTo(0,0)")
    print("検索完了")

    element = WebDriverWait(driver, 10).until(
    expected_conditions.presence_of_element_located((By.ID, "search_medical_table_radio_0"))
    )

    #会場コードを取得
    f = open('config.json','r')
    j=json.load(f)
    place_list=j["date"]["place"]
    f.close()
    place_page=int(list(str(place_list[0]))[0])
    place_num=int(list(str(place_list[0]))[1])


    print("番号取得完了")

    #ページ選択
    for i in range(place_page):
        driver.find_element(By.LINK_TEXT, "次").click()

    #会場番号選択
    driver.find_element(By.ID, "search_medical_table_radio_"+place_num).click()
    #会場確定
    driver.find_element(By.ID, "btn_select_medical").click()

    #gennzai日付取得
    now_time=ntp_now('ntp.nict.jp')
    now_year=int(now_time[0:4])
    now_month=int(now_time[6:7])
    now_date=int(now_time[9:10])

    #予約する日付取得
    f = open('config.json','r')
    j=json.load(f)
    date_year=int(j["date"]["year"])
    date_list=j["date"]["date_list"]
    f.close()

    for i in date_list:
        date_i=(date_list[i])
        month_i=int(date_i[0:1])
        selmonth=now_month-month_i
        print(selmonth)

        #月選択
        for i in range(selmonth):
            driver.find_element(By.CSS_SELECTOR, "#calendar .fc-right .fa").click()

        #ここの番号1から始まるので注意
        def get_nth_week2(year, month, day, firstweekday=0):
            first_dow = calendar.monthrange(year, month)[0]
            offset = (first_dow - firstweekday) % 7
            return (day + offset - 1) // 7 + 1,calendar.weekday(year, month, day)

        res_num_tuple=get_nth_week2(date_year,month_i,date_i)

        week_num=res_num_tuple[0]
        date_num=res_num_tuple[1]+1
        res_mark_text=driver.find_element_by_xpath("//*[@id='calendar]/div[2]/div/table/tbody/tr/td/div/div/div["+week_num+"]/div[2]/table/thead/tr/td["+date_num+"]").get_attribute("td")

        print(res_mark_text)

        

        #日付クリック
        driver.find_element(By.CSS_SELECTOR, ".fc-row:nth-child(3) > .fc-bg .fc-tue").click()

        #時間クリック
        driver.find_element(By.CSS_SELECTOR, "td:nth-child(4) > .fc-bg-reserved > div").click()

    #予約を確定する
    driver.find_element(By.ID, "btn_reservation_entry").click()
     
     
    # ブラウザ停止
    driver.quit()
