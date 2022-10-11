#사용된 import / pip download시 참고
# 내장 모듈 - re, time, os, datatime
# pip install smtplib
# pip install schedule
# pip install selenium
# pip install webdriver-manager

import re
import time
import os
import smtplib
from datetime import datetime as dt
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import schedule


#SATCAT 다운로드시 file name
satcat_file_name = 'https___www.space-track.org_basicspacedata_query_class_satcat_orderby_norad_cat_id asc_format_csv_emptyresult_show.csv'

downloadPath = "C:\\Users\\{}\\Desktop\\Space\\reproccess_TLE".format(os.getlogin()) #작업이 이루어질 dir


email_id = ''   #SMTP에서 사용할 id // gmail 혹은 naver만 가능하며 gamil의 경우 2차 비밀번호 설정해야 가능
email_pw = ''   #SMTP에서 사용할 비밀번호 // gamil의 경우 2차 비밀번호
to_mail = [""] #STMP를 사용하여 발신할 목록

spacetrack_id = '' #spacetrack에서 사용할 id
spacetrack_pw = '' #spacetrack에서 사용할 비밀번호

# payload - rcs(large) 외 추가할 예외 인공물체
default_check_list = [
    "",
]


switch = False  #schedule 모듈을 사용하기위한 트리거 전역변수


def check_Path(downloadPath=downloadPath):   # dir 존재 유무 후 없을시 폴더 생성
    if os.path.isdir(downloadPath): pass
    else: os.makedirs(downloadPath)


def sorting_TLE(tle=list):  #TLE 각 라인별 정렬 / 다운로드한 TLE를 2차원 리스트로 선언 후 다시 TLE를 파일쓰기 할때 사용된다.
    if tle[0]=='0':
        return tle

    elif tle[0]=='1':
        tle[0] = str(tle[0])
        tle[1] = str(tle[1]).rjust(6,' ')
        tle[2] = str(tle[2]).ljust(8,' ')
        tle[3] = str(tle[3])
        tle[4] = str(tle[4]).rjust(10,' ')
        tle[5] = str(tle[5]).rjust(8,' ')
        tle[6] = str(tle[6]).rjust(8,' ')
        tle[7] = str(tle[7])
        tle[8] = str(tle[8]).rjust(5,' ')
        return tle

    elif tle[0]=='2':
        tle[0] = str(tle[0])
        tle[1] = str(tle[1]).rjust(5,' ')
        tle[2] = str(tle[2]).rjust(8,' ')
        tle[3] = str(tle[3]).rjust(8,' ')
        tle[4] = str(tle[4])
        tle[5] = str(tle[5]).rjust(8,' ')
        tle[6] = str(tle[6]).rjust(8,' ')
        if len(tle) == 8:
            tle[7] = str(tle[7]).rjust(17,' ')
        elif len(tle) == 9:
            tle[7] = str(tle[7]).rjust(11,' ')
            tle[8] = str(tle[8]).rjust(5,' ')
        return tle
    else: return False


def check_name(sat_name=str,check_list=list): #TLE 중 TBA 등 필요 없는 라인은 삭제
    if not str(sat_name).find("T"):     #T로 시작하는 TLE는 가공하지 않음
        pass
    elif sat_name in check_list:     #Check_list에 존재하는 TLE는 가공하지 않음
        return False
    else:
        temp = str(sat_name).replace("U","")    #해당 작업은 00001U 와 같은 Norad를 1U로 변경해주는 작업임
        temp = int(temp)                        #이 부분에서 00001(str) -> 1(int)로 변경
        temp = str(temp) + "U"
        if temp in check_list:
            return False
    return True


def sending_mail(to_mail=to_mail): #재처리 완료된 TLE를 메일로 전송
    f_year = str(dt.now().year)
    f_month = '{:0>2}'.format(str(dt.now().month))
    f_day = '{:0>2}'.format(str(dt.now().day))

    togo_file_name = f_year+f_month+f_day+"_TLE(re).txt"
    msg_title = f_year+f_month+f_day+"_TLE"

    recipients = []
    for mail in to_mail:
        recipients.append(mail)

    msg = MIMEMultipart()
    msg['Subject'] = msg_title
    msg['From'] = email_id
    msg['To'] = ",".join(recipients)

    content = """
        <html>
            <body>
                본문 내용
            </body>
        </html>
    """

    mimetext = MIMEText(content, 'html')
    msg.attach(mimetext)


    file_name = downloadPath + '\\TLE(re).txt'
    with open(file_name, 'rb') as excel_file : 
        attachment = MIMEApplication( excel_file.read() )
        attachment.add_header('Content-Disposition','attachment', filename=togo_file_name) 
        msg.attach(attachment)


    if re.search("@gmail.com", email_id):
        server = smtplib.SMTP('smtp.gmail.com', 587) #587 #465
    else:
        server = smtplib.SMTP('smtp.naver.com', 587) #587 #465 

    server.ehlo()
    server.starttls()
    server.login(email_id,email_pw)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    print("메일 전송 완료\t ",dt.now())


def extract_checklist(): #SATCAT 및 default_check_list를 참고하여 check_list 생성
    r = open(downloadPath+"\\"+satcat_file_name, "r")
    line = r.read().splitlines()

    temp = []
    for i in range(len(line)):
        ret = line[i].replace('"',"")
        ret = list(ret.split(","))
        temp.append(ret)
    r.close()


    check_list = []

    global default_check_list
    for i in default_check_list:
        check_list.append(str(i)+"U")

    for i in range(len(temp)):          #PAYLOAD 중에서 RCS가 LARGE, MEDIUM 그리고 STARLINK 종류는전부 check_list에 포함
        if temp[i][2]=="PAYLOAD": 
            if temp[i][15]=="LARGE":
                check_list.append(str(temp[i][1])+"U")
            elif not str(temp[i][3]).find("STARLINK"):
                check_list.append(str(temp[i][1])+"U")



    check_list = list(set(check_list))
    check_list.sort()

    w = open(downloadPath+"\\"+"check_list.txt", "w", encoding="utf-8")
    for i in check_list:
        w.write(str(i))
        w.write("\n")
        
    w.write(str(dt.today()))
    w.close()

    print("check_list 추출 완료\t ",dt.now())
    return check_list


def download_file(): #TLE와 check_list 생성을 위한 SATCAT 다운로드

    if os.path.isfile(downloadPath+"\\"+satcat_file_name): #기존의 더미데이터가 존재한다면 삭제해주는 부분
        os.remove(downloadPath+"\\"+satcat_file_name)

    file_list = os.listdir(downloadPath)

    for i in file_list:
        if re.search(".crdownload", i):
            os.remove(downloadPath+"\\"+i)


    options = Options()
    options.headless = False    #headless를 True로 설정하면 진행되는 동안 크롬 창이 출력되지 않으나 오류에 걸릴 수도 있음
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    options.add_argument('user-agent=' + user_agent)
    options.add_experimental_option('prefs',{'download.default_directory':downloadPath})


    browser = webdriver.Chrome(ChromeDriverManager().install(),options=options)
    time.sleep(1)
    browser.get("https://www.space-track.org/auth/login")
    browser.implicitly_wait(10)

    time.sleep(1)
    browser.find_element(By.XPATH, '//*[@id="identity"]').click()

    time.sleep(1)
    browser.find_element(By.ID, "identity").send_keys(spacetrack_id)

    time.sleep(1)
    browser.find_element(By.XPATH, '//*[@id="password"]').click()
    time.sleep(1)

    browser.find_element(By.ID, "password").send_keys(spacetrack_pw)
    time.sleep(5)

    browser.find_element(By.XPATH, '//*[@id="login-panel-body"]/form/div[3]/input').click()
    browser.implicitly_wait(10)


    browser.get("https://www.space-track.org/basicspacedata/query/class/satcat/orderby/NORAD_CAT_ID asc/format/csv/emptyresult/show")
    time.sleep(3)

    browser.get("https://www.space-track.org/basicspacedata/query/class/gp/EPOCH/%3Enow-30/orderby/NORAD_CAT_ID,EPOCH/format/3le")
    browser.implicitly_wait(10)
    line_3 = browser.page_source
    time.sleep(1)

    ret = line_3.replace('<html><head><meta name="color-scheme" content="light dark"></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">',"")
    ret = ret.replace('</pre></body></html>',"")

    time.sleep(1)
    w = open(downloadPath+"\\3le.txt", "w", encoding="utf8")
    w.write(ret)
    w.close()
 
    time.sleep(1)
    print("파일 다운로드 완료\t ",dt.now())


def trans_TLE(check_list): #check_list를 받아서 실질적으로 재처리가 진행되는 부분
    r = open(downloadPath+"\\"+"3le.txt", "r", encoding="utf-8")
    line = r.read().splitlines()
    temp = []
    for i in range(len(line)):
        temp.append(line[i].split())
    r.close()

    for i in range(1,len(temp),3):
        if check_name(temp[i][1],check_list):
            temp[i][3] = '22001.00000000'  #해당 부분을 수정하면 다른 부분의 TLE도 임의로 수정 가능

    w = open(downloadPath+"\\"+"TLE(re).txt", "w", encoding="utf-8")

    for i in range(len(temp)):
        if temp[i][1] == "TBA": # 81XXX TBA 제외
            p = re.compile("^81")
            if p.match(str(temp[i+1][1])):break

        sorting_TLE(temp[i]) # 파일 쓰기를 위한 TLE 정렬
        w.write(' '.join(map(str, temp[i])))
        w.write("\n")

    w.close()
    print("TLE 가공 완료\t ",dt.now())


def job(): #schedule 모듈을 사용하기 위한 트리거
    print("예약된 시간이 되어 작업을 시작합니다.\t ",dt.now())
    global switch
    switch = True


def t_clear(): #터미널 클리어
    os.system('cls')
    print("터미널 clear\t ",dt.now())



schedule.every().day.at("00:00").do(job) # Sechdule 모듈을 사용하여 실행 시간 설정
schedule.every(3).days.do(t_clear)  # 터미널 Clear


if __name__=="__main__":
    print("실행\t ",dt.now())

    while True:
        schedule.run_pending()
        # switch = True #디버깅시 schedule 모듈을 기다리지 않고 바로 시작할때 사용
        try:
            if switch:
                start_time = dt.now()
                check_Path()
                download_file()
                check_list = extract_checklist()
                trans_TLE(check_list)
                sending_mail()
                del check_list
                end_time = dt.now()

                print("소요시간: ",end_time-start_time)
                print("현재시간: ",dt.now())
                switch = False
            else:
                time.sleep(30)
        except:
            time.sleep(180)
