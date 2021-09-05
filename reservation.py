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
import chromedriver_binary

def ntp_now(server, port = 123):

    with socket(AF_INET, SOCK_DGRAM) as s:
        s.sendto(b'\x1b' + 47 * b'\0', (server, port))
        result = s.recvfrom(1024)[0]
    if result:
        return datetime.fromtimestamp(unpack(b'!12I', result)[10] - 2208988800)
    else:
        None

def click(driver, attribute, str):
    element = WebDriverWait(driver, config["timeout"]).until(
        expected_conditions.presence_of_element_located((attribute, str))
    )
    driver.find_element(attribute, str).click()

def chk_time_table(driver):

    #時間取得
    time_list=config["date"]["time_list"]

    n_time=0
    for i in time_list:
        element = WebDriverWait(driver, config["timeout"]).until(
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


        print(time_num_i,"は",res_mark_text_time,"です。")

        if res_mark_text_time == "×":
            n_time=n_time+1
            continue

        else:
            click(driver, By.XPATH, "//*[@id='dayly-calendar-table']/tbody/tr["+str(uekara_num+1)+"]/td["+str(migikara_num)+"]/div/div")

            #予約を確定する
            time.sleep(3)
            driver.execute_script("window.scrollTo(0,1100);")

            click(driver, By.ID, "btn_reservation_entry")

            element = WebDriverWait(driver, config["timeout"]).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="modal-input-reserve-error-message-btn"]'))
            )
            time.sleep(3)
            
            #確定時にエラーが発生した場合時間選択処理を中止し、カレンダー画面に遷移させた後、chk_calenderにもどります。
            if len(driver.find_elements_by_xpath('//*[@id="modal-input-reserve-error-message-btn"]/p')) > 0:
                driver.find_element(By.ID, "btn_reservation_back").click()
                assert driver.switch_to.alert.text == "3020e003:予約は登録（又は変更）されていませんが、中止してよろしいでしょうか。"
                driver.switch_to.alert.accept()
                click(driver, By.ID, "btn_select_Date")
                time.sleep(1)
                element = WebDriverWait(driver, config["timeout"]).until(
                expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#calendar .fc-right .fa"))
                )
                return False
               
            else:
                print("予約が完了しました")
                driver.quit()
                return True

    #カレンダー表示に戻してからchk_calenderに戻ります。
    click(driver, By.ID, "month")
    time.sleep(1)
    element = WebDriverWait(driver, config["timeout"]).until(
    expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#calendar .fc-right .fa"))
    )
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
    date_year=int(config["date"]["year"])
    date_list=config["date"]["date_list"]

    n=0
    for i in date_list:

        #予約する日付
        date_num_i=(date_list[n])
        print("-------------------------")
        print(date_num_i,"の予約処理を行います")
        month_i=int(date_num_i[0:2])
        date_i=int(date_num_i[2:4])
        day_out=date_num_i

        #予約する日時のdatetime作成
        res_datetime_str = str(date_year)+"-"+str(month_i)+"-"+str(date_i)+" 00:00:01"
        res_datetime = datetime.strptime(res_datetime_str, '%Y-%m-%d %H:%M:%S')
        #予約可能期間か確認
        td=res_datetime-now_datetime
        print("予約日-本日は",td.days , "日です。")
        if td.days < 0:
            print("configの日付が古いです。実行に問題はありませんが処理が遅くなります。古い日付を削除することをお勧めします。")
            n=n+1
            continue

        #デバッグ時は数字を大きくしてください。
        if int(td.days) <= config["date"]["limit"]:

            selmonth=month_i-now_month

            #月選択処理
            #予約月-今月 分カレンダーを右にしています。
            for i in range(selmonth):
                click(driver, By.CSS_SELECTOR, "#calendar .fc-right .fa")
            now_month = month_i

            #目的の日付がテーブルのどこにあるかを処理しています。
            #ここの番号1から始まるので注意
            def get_nth_week2(year, month, day, firstweekday=0):
                first_dow = calendar.monthrange(year, month)[0]
                offset = (first_dow - firstweekday) % 7
                return (day + offset - 1) // 7 + 1,calendar.weekday(year, month, day)

            res_num_tuple=get_nth_week2(date_year,month_i,date_i)

            week_num=res_num_tuple[0]
            date_num_i=res_num_tuple[1]+1
            #デバッグ用、上から、右から何番目かの数字
            print(week_num,date_num_i)

            time.sleep(2)
            
            try:
                #○×の要素があるか確認。会場によっては空欄のことがあるので。
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
            
            print(day_out,"は",res_mark_text,"です")

            if res_mark_text != "〇" and res_mark_text != "△":
                n=n+1
                continue

            else:
                #日付クリック
                click(driver, By.XPATH, '//*[@id="calendar"]/div[2]/div/table/tbody/tr/td/div/div/div['+str(week_num)+']/div[1]/table/tbody/tr/td['+str(date_num_i)+']')

                if chk_time_table(driver):
                    return True
                else:
                    n=n+1
                    continue
        else:
            n=n+1
            continue
    print("-------------------------")
    return False

def select_medical(driver):

    #検索ボタン
    click(driver, By.ID, "btn_search_medical")

    #多分検索処理？
    element = driver.find_element(By.ID, "btn_search_medical")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    element = driver.find_element(By.CSS_SELECTOR, "body")
    actions = ActionChains(driver)
    driver.execute_script("window.scrollTo(0,0)")
    print("接種会場一覧検索完了")

    try:
        element = WebDriverWait(driver, config["timeout"]).until(
        expected_conditions.presence_of_element_located((By.ID, "search_medical_table_radio_0"))
        )
    except:
        #検索結果に出てこない = 空きがない
        return False
    
    return True

def reserve():
     
    options = Options()
    if config["headless"]:
        # ヘッドレスモードでブラウザを起動
        options.add_argument('--headless')
 
    # ブラウザーを起動
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1280,720)
    # urlにアクセス
    driver.get(config["url"])

    #接種券番号、パスワードを入力
    ticket_number=config["account"]["number"]
    password=config["account"]["pass"]
    print("アカウント情報取得完了")

    element = WebDriverWait(driver, config["timeout"]).until(
    expected_conditions.presence_of_element_located((By.ID, "login_id"))
    )

    driver.execute_script("window.scrollTo(0,2900);")
    time.sleep(1)
    driver.find_element_by_xpath("//*[@id='login_id']").send_keys(ticket_number)
    driver.find_element(By.ID, "login_pwd").send_keys(password)
    print("アカウント情報入力完了")
    click(driver, By.ID, "btn_login")
    

    element = WebDriverWait(driver, config["timeout"]).until(
    expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#mypage_accept font"))
    )
    if len(driver.find_elements(By.CSS_SELECTOR, "#mypage_accept font")) > 0:
        print("ログイン完了")
        #予約・変更するボタン
        click(driver, By.CSS_SELECTOR, "#mypage_accept font")
        print("予約ページ遷移完了")
        
        driver.execute_script("window.scrollTo(0,870);")
        #接種会場を選択ボタン
        time.sleep(1)
        click(driver, By.CSS_SELECTOR, "#btn_Search_Medical > font")
        print("接種会場ページ遷移完了")
        print("-------------------------")

        for medical in config["medical"]:

            element = WebDriverWait(driver, config["timeout"]).until(
            expected_conditions.presence_of_element_located((By.ID, "reserve_status_check"))
            )
            if config["mode"] != 1:
                if driver.find_element(By.ID, "reserve_status_check").is_selected() == True:
                    click(driver, By.ID, "reserve_status_check")
            else:
                if driver.find_element(By.ID, "reserve_status_check").is_selected() == False:
                    click(driver, By.ID, "reserve_status_check")

            #会場名を入力
            element = WebDriverWait(driver, config["timeout"]).until(
            expected_conditions.presence_of_element_located((By.ID, "medical_institution_name"))
            )
            driver.find_element(By.ID, "medical_institution_name").clear()
            driver.find_element(By.ID, "medical_institution_name").send_keys(medical["name"])

            time.sleep(1)
            element = WebDriverWait(driver, config["timeout"]).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#btn_Search_Medical > font"))
            )
            
            if config["mode"] == 1:
                limit = config["limit"]
                place_page = place_num = 0
            else:
                limit = 1
                place_page=int(medical["index"]/10)
                place_num=medical["index"]-(place_page*10)
            for retry_cnt in range(limit):
                ret = select_medical(driver)
                if ret:
                    break                   
                time.sleep(config["interval"])
            if ret == False:
                continue

            #ページ選択
            for i in range(place_page):
                click(driver, By.LINK_TEXT, "次")

            #会場番号選択
            click(driver, By.ID, "search_medical_table_radio_"+str(place_num))
            #会場確定
            click(driver, By.ID, "btn_select_medical")

            if config["mode"] == 2:
                limit = config["limit"]
            else:
                limit = 1
            for retry_cnt in range(limit):
                if chk_calendar(driver):
                    exit()
                    
                # カレンダーを閉じる
                try:
                    element = WebDriverWait(driver, config["timeout"]).until(
                    expected_conditions.presence_of_element_located((By.XPATH,'//*[@id="calendar"]/div[2]/div/table/tbody/tr/td/div/div/div[2]/div[2]/table/thead/tr/td[2]/span[2]'))
                    )
                except:
                    time.sleep(3)
                    
                click(driver, By.ID, "btn_calender_modal_close")
                if retry_cnt != limit - 1:
                    time.sleep(config["interval"])
                    # カレンダーを開き直す(最新の情報が取得される)
                    click(driver, By.ID, "btn_select_Date")
                    time.sleep(1)

            #接種会場を選択ボタン
            time.sleep(1)
            driver.execute_script("window.scrollTo(0,900);")
            time.sleep(1)

            element = WebDriverWait(driver, config["timeout"]).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#btn_Search_Medical > font"))
            )
            click(driver, By.CSS_SELECTOR, "#btn_Search_Medical > font")
            print("接種会場ページ遷移完了")


    else:
        print("ログインエラーまたはメンテナンス中です")
    
        
    # ブラウザ停止
    driver.quit()

schedule.every(1).hour.do(reserve)
schedule.every().day.at("00:00").do(reserve)

f = open('config/config.json','r',encoding="utf-8")
config=json.load(f)
f.close()

reserve()

if config["mode"] == 0:
    while True:
        schedule.run_pending()
        time.sleep(60)
        

