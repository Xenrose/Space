# 내장 모듈 - time, os, datetime
# pip install pandas
# pip install wbdriver-manager
# pip install selenium

import pandas as pd
import time
from datetime import datetime as dt
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import matplotlib.pyplot as plt


downloadPath = "C:\\Users\\{}\\Desktop\\Space\\analysis_TLE".format(os.getlogin()) #작업이 이루어질 dir

spacetrack_id = ""          # TLE 다운을 위한 spacetarck id
spacetrack_password = ""    # TLE 다운을 위한 spacetrack pw





def check_Path(downloadPath=downloadPath):   # dir 존재 유무 후 없을시 폴더 생성
    if os.path.isdir(downloadPath): pass
    else: os.makedirs(downloadPath)


def download_file(tle_list):                # 분석할 TLE가 담긴 list를 파라미터로 받아 해당 tle를 자동으로 다운로드
    options = Options()                     # 단, spacetrack 정책상 1시간에 60개 이상의 tle 다운로드는 지양
    options.headless = False
    # https://www.whatismybrowser.com/detect/what-is-my-user-agent/
    # 위 주소에서 user_agent를 확인 가능
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    options.add_argument('user-agent=' + user_agent)
    options.add_experimental_option('prefs',{'download.default_directory':downloadPath})


    browser = webdriver.Chrome(ChromeDriverManager().install(),options=options)
    time.sleep(1)
    browser.get("https://www.space-track.org/auth/login")
    browser.implicitly_wait(10)

    time.sleep(1)
    browser.find_element_by_xpath('//*[@id="identity"]').click()
    time.sleep(1)
    browser.find_element(By.ID, "identity").send_keys(spacetrack_id)

    time.sleep(1)
    browser.find_element_by_xpath('//*[@id="password"]').click()
    time.sleep(1)

    browser.find_element(By.ID, "password").send_keys(spacetrack_password)
    time.sleep(1)

    browser.find_element_by_xpath('//*[@id="login-panel-body"]/form/div[3]/input').click()
    browser.implicitly_wait(10)

    for tle in tle_list:
        browser.get("https://www.space-track.org/basicspacedata/query/class/tle/NORAD_CAT_ID/"+str(tle)+"/orderby/EPOCH asc/format/tle/emptyresult/show")
        browser.implicitly_wait(60)
        line_3 = browser.page_source
        time.sleep(1)

        ret = line_3.replace('<html><head><meta name="color-scheme" content="light dark"></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">',"")
        ret = ret.replace('</pre></body></html>',"")

        time.sleep(1)
        w = open(downloadPath+"\\TLE_raw\\"+str(tle)+".txt", "w", encoding="utf8") # norad 번호 입력
        w.write(ret)
        w.close()

    time.sleep(1)
    print("파일 다운로드 완료\t ",dt.now())

def ex_tle(tle,index):      # tle 중 line2 정보가 담긴 list를 파라미터로 입력받고 tle[index]를 반환
    if tle[0] == '2':       # tle[index]는 inclination. RAAN, aop 등의 사용자가 필요로 하는 tle 정보
        return tle[index]

def ex_all_figure(norad,tle_name):      # download한 tle를 읽어서 2차원 list로 만든 뒤 
    filename = str(norad)               # 하나씩 요소를 분석하여 matplot을 통해 시각화 하는 함수
    r = open(downloadPath +"\\TLE_raw\\" + filename + ".txt", "r", encoding="utf8")
    line = r.read().splitlines()
    temp = []

    for i in range(len(line)):
        temp.append(line[i].split())

    inclination = []        # inclination = 2
    RAAN = []               # RAAN = 3
    aop = []                # aop = argument of perigee = 5
    mean_anomaly = []       # mean anomaly = 6
    mean_motion = []        # mean motion = 7

    for i in temp:
        if ex_tle(i,2): inclination.append(float(ex_tle(i,2)))

    for i in temp:
        if ex_tle(i,3): RAAN.append(float(ex_tle(i,3)))

    for i in temp:
        if ex_tle(i,5): aop.append(float(ex_tle(i,5)))

    for i in temp:
        if ex_tle(i,6): mean_anomaly.append(float(ex_tle(i,6)))

    for i in temp:
        if ex_tle(i,7): mean_motion.append(float(ex_tle(i,7)))

    incli_reverse = []
    for i in range(len(inclination)-1,0,-1):
        ret = inclination[i] - inclination[i-1]
        incli_reverse.append(ret)

    incli_reverse.reverse()
    df_incl = pd.DataFrame(incli_reverse).tail(200)
    df_RAAN = pd.DataFrame(RAAN).tail(200)
    df_aop = pd.DataFrame(aop).tail(200)
    df_mean_anomaly = pd.DataFrame(mean_anomaly).tail(200)
    df_mean_motion = pd.DataFrame(mean_motion).tail(200)

    plt.plot(df_incl, label='inclination')
    plt.plot(df_RAAN, label='RAAN')
    plt.plot(df_aop, label='aop')
    plt.plot(df_mean_anomaly, label='mean anomaly')
    plt.plot(df_mean_motion, label='mean motion')
    
    plt.title(str(tle_name[norad])+"_all")
    plt.ylabel('all', labelpad=20)
    plt.legend(loc=(0.2,1.0), ncol=2)

    plt.savefig(downloadPath +"\\all\\"+ filename + "_all.png", format='png', dpi=200)
    plt.clf()


if __name__=="__main__":
    start_time = dt.now()
    tle_list = [52894,52895,52896,52897,52898,52899,52900,
    25544,48274, # iss, css
    44918,47379,49446, # starlink 1099, 2099, 3099
    23186,23828,25138,25242, # CZ-3 RB, PSLV RB, DELTA 2 DEB, IRIDUM 53 DEB
    ]

    tle_name = {
        52894:'PVSAT',
        52895:'KSLV DUMMY SAT',
        52896:'KSLV-2 RB',
        52897:'CHOSUN UNI.',
        52898:'KAIST UNI.',
        52899:'SEOUL UNI.',
        52900:'YONSEI UNI.',
        25544:'ISS',
        48274:'CSS',
        44918:'STARLINK-1099',
        47379:'STARLINK-2099',
        49446:'STARLINK-3099',
        23186:'CZ-3 RB',
        23828:'PSLV RB',
        25138:'DELTA 2 DEB',
        25242:'IRIDUM 53 DEB'
    }


    for tle in tle_list:
        ex_all_figure(tle,tle_name)

    print("실행 완료")
    end_time = dt.now()
    print("실행시간: ",end_time-start_time)    