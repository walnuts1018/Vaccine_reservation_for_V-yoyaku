from io import DEFAULT_BUFFER_SIZE
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
import schedule
import subprocess
import platform

CHROMEDRIVER = "/usr/bin/chromedriver"
WEB_WAIT_TIME = 10
RETRY_MAX_CNT = 100
RETRY_WAIT_TIME = 60

def ntp_now(server, port = 123):

    with socket(AF_INET, SOCK_DGRAM) as s:
        s.sendto(b'\x1b' + 47 * b'\0', (server, port))
        result = s.recvfrom(1024)[0]
    if result:
        return datetime.fromtimestamp(unpack(b'!12I', result)[10] - 2208988800)
    else:
        None

def chk_time_table(driver):

    #時間取得
    f = open('config.json','r',encoding="utf-8")
    j=json.load(f)
    time_list=j["date"]["time_list"]
    f.close()

    n_time=0
    for i in time_list:
        element = WebDriverWait(driver, WEB_WAIT_TIME).until(
        expected_conditions.presence_of_element_located((By.XPATH,"//*[@id='dayly-calendar-table']/tbody/tr[2]/th/div/span"))
        )
        time.sleep(1)
        start_hour=driver.find_element(By.XPATH,"//*[@id='dayly-calendar-table']/tbody/tr[2]/th/div/span").text
        time_num_i=(time_list[n_time])
        hour_i=int(time_num_i[0:2])
        min_i=int(time_num_i[2:4])
        migikara_num=round(min_i/15)+1
        uekara_num=hour_i-int(start_hour)+1

        if uekara_num < 1:
            continue

        if len(driver.find_elements(By.XPATH, "//*[@id='dayly-calendar-table']/tbody/tr["+str(uekara_num+1)+"]/td["+str(migikara_num)+"]/div/div")) > 0:
            res_mark_text_time=driver.find_element(By.XPATH, "//*[@id='dayly-calendar-table']/tbody/tr["+str(uekara_num+1)+"]/td["+str(migikara_num)+"]/div/div").text

        else:
            res_mark_text_time="×"


        print(res_mark_text_time)

        if res_mark_text_time == "×":
            n_time=n_time+1
            continue

        else:
            driver.find_element(By.XPATH, "//*[@id='dayly-calendar-table']/tbody/tr["+str(uekara_num+1)+"]/td["+str(migikara_num)+"]/div/div").click() 

            #予約を確定する
            time.sleep(3)
            element = WebDriverWait(driver, WEB_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.ID, "btn_reservation_entry"))
            )
            driver.execute_script("window.scrollTo(0,1100);")

            #driver.find_element(By.XPATH, '//*[@id="btn_reservation_entry"]/i').click()
            driver.find_element(By.ID, "btn_reservation_entry").click()

            element = WebDriverWait(driver, WEB_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="modal-input-reserve-error-message-btn"]'))
            )
            time.sleep(3)
            
            if len(driver.find_elements_by_xpath('//*[@id="modal-input-reserve-error-message-btn"]/p')) > 0:
                break
                
            else:
                print("予約が完了しました")
                driver.quit()
                return True

    return False

def chk_calendar(driver):

    #gennzai日付取得
    now_datetime=ntp_now('ntp.nict.jp')
    now_time=str(now_datetime)
    now_year=int(now_time[0:4])
    now_month=int(now_time[5:7])
    now_date=int(now_time[8:10])
    print(now_datetime)

    #予約する日付取得
    f = open('config.json','r',encoding="utf-8")
    j=json.load(f)
    date_year=int(j["date"]["year"])
    date_list=j["date"]["date_list"]
    f.close()

    n=0
    for i in date_list:

        #予約する日付
        date_num_i=(date_list[n])
        print(date_num_i)
        month_i=int(date_num_i[0:2])
        date_i=int(date_num_i[2:4])
        print(month_i,date_i)

        #予約する日時のdatetime作成
        res_datetime_str = str(date_year)+"-"+str(month_i)+"-"+str(date_i)+" 00:00:01"
        res_datetime = datetime.strptime(res_datetime_str, '%Y-%m-%d %H:%M:%S')
        #予約可能期間か確認
        td=res_datetime-now_datetime
        print("予約日-本日=",td.days , "20以上なら予約処理されません")
        if td.days < 1:
            print("configの日付が古いです")
            n=n+1
            continue

        #本来20日(余裕をもって21にしてみる)
        if int(td.days) <=21:

            selmonth=month_i-now_month

            element = WebDriverWait(driver, WEB_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#calendar .fc-right .fa"))
            )
            #月選択

            for i in range(selmonth):
                driver.find_element(By.CSS_SELECTOR, "#calendar .fc-right .fa").click()
            now_month = month_i

            #ここの番号1から始まるので注意
            def get_nth_week2(year, month, day, firstweekday=0):
                first_dow = calendar.monthrange(year, month)[0]
                offset = (first_dow - firstweekday) % 7
                return (day + offset - 1) // 7 + 1,calendar.weekday(year, month, day)

            res_num_tuple=get_nth_week2(date_year,month_i,date_i)

            week_num=res_num_tuple[0]
            date_num_i=res_num_tuple[1]+1
            print(week_num,date_num_i)

            time.sleep(2)
            
            try:
                element = WebDriverWait(driver, 1).until(
                expected_conditions.presence_of_element_located((By.XPATH,'//*[@id="calendar"]/div[2]/div/table/tbody/tr/td/div/div/div['+str(week_num)+"]/div[2]/table/thead/tr/td["+str(date_num_i)+"]/span[2]"))
                )
            except:
                #指定した日付が空欄だった場合
                n=n+1
                continue
                
            if len(driver.find_elements(By.XPATH,'//*[@id="calendar"]/div[2]/div/table/tbody/tr/td/div/div/div['+str(week_num)+"]/div[2]/table/thead/tr/td["+str(date_num_i)+"]/span[2]")) > 0:
                res_mark_text=driver.find_element(By.XPATH,'//*[@id="calendar"]/div[2]/div/table/tbody/tr/td/div/div/div['+str(week_num)+"]/div[2]/table/thead/tr/td["+str(date_num_i)+"]/span[2]").text

            else:
                n=n+1
                continue
            
            print(res_mark_text)

            if res_mark_text != "〇" and res_mark_text != "△":
                n=n+1
                continue

            else:
                #日付クリック
                driver.find_element(By.XPATH, '//*[@id="calendar"]/div[2]/div/table/tbody/tr/td/div/div/div['+str(week_num)+']/div[1]/table/tbody/tr/td['+str(date_num_i)+']').click()

                if ChkTimeTable(driver):
                    return True
                n=n+1
                continue
        else:
            n=n+1
            continue

    return False

def select_medical(driver):

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

    try:
        element = WebDriverWait(driver, WEB_WAIT_TIME).until(
        expected_conditions.presence_of_element_located((By.ID, "search_medical_table_radio_0"))
        )
    except:
        #検索結果に出てこない = 空きがない
        return False
    
    return True

def reserve():

    url = "https://v-yoyaku.jp/341002-hiroshima"
     
    #　ヘッドレスモードでブラウザを起動
    options = Options()
    #GUIで実行を確認する場合下の一行をコメントアウト
    options.add_argument('--headless')
 
    # ブラウザーを起動
    driver = webdriver.Chrome(CHROMEDRIVER, options=options)
     
    # urlにアクセス
    driver.get(url)

    #接種券番号、パスワードを入力
    f = open('config.json','r',encoding="utf-8")
    j=json.load(f)
    ticket_number=j["ID"]["number"]
    password=j["ID"]["pass"]
    f.close()
    print("login情報取得完了")

    element = WebDriverWait(driver, WEB_WAIT_TIME).until(
    expected_conditions.presence_of_element_located((By.ID, "login_id"))
    )

    driver.execute_script("window.scrollTo(0,2900);")
    time.sleep(1)
    #driver.find_element(By.ID, "login_id").click()
    driver.find_element_by_xpath("//*[@id='login_id']").send_keys(ticket_number)
    #driver.find_element(By.ID, "login_pwd").click()
    driver.find_element(By.ID, "login_pwd").send_keys(password)
    print("入力完了")
    driver.find_element_by_xpath("//*[@id='btn_login']").click()
    

    element = WebDriverWait(driver, WEB_WAIT_TIME).until(
    expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#mypage_accept font"))
    )
    if len(driver.find_elements(By.CSS_SELECTOR, "#mypage_accept font")) > 0:
        print("ログイン完了")
        #予約・変更するボタン
        driver.find_element(By.CSS_SELECTOR, "#mypage_accept font").click()
        print("予約ページ遷移完了")
        
        element = WebDriverWait(driver, WEB_WAIT_TIME).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#btn_Search_Medical > font"))
        )

        driver.execute_script("window.scrollTo(0,870);")
        #接種会場を選択ボタン
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, "#btn_Search_Medical > font").click()
        print("接種会場ページ遷移完了")

        time.sleep(1)
        element = WebDriverWait(driver, WEB_WAIT_TIME).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#btn_Search_Medical > font"))
        )
        
        for retry_cnt in range(RETRY_MAX_CNT):
            if SelectMedical(driver):
                break
            time.sleep(RETRY_WAIT_TIME)

        #会場コードを取得
        f = open('config.json','r',encoding="utf-8")
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
        driver.find_element(By.ID, "search_medical_table_radio_"+str(place_num)).click()
        #会場確定
        driver.find_element(By.ID, "btn_select_medical").click()

        if ChkCalendar(driver):
            exit()

    else:
        print("ログインエラーまたはメンテナンス中です")
    
        
    # ブラウザ停止
    driver.quit()

"""     
    pf = platform.system()
    if pf == 'Windows':
        try:
            res = subprocess.check_call("taskkill /im chromedriver")
        except:
            print("Chromeプロセスを終了できませんでした。エラーが出た場合pkill chromeを実行してください。")

    elif pf == 'Darwin':
        try:
            res = subprocess.check_call("pkill chromedriver")
        except:
            print("Chromeプロセスを終了できませんでした。エラーが出た場合pkill chromeを実行してください。")

    elif pf == 'Linux':
        try:
            res = subprocess.check_call("pkill chromedriver")
        except:
            print("Chromeプロセスを終了できませんでした。エラーが出た場合pkill chromeを実行してください。")
"""



schedule.every(1).hour.do(reserve)
schedule.every().day.at("12:00").do(reserve)


reserve()
while True:
    schedule.run_pending()
    time.sleep(60)
    

