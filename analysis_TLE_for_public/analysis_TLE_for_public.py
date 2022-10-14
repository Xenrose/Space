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

spacetrack_id = ""
spacetrack_password = ""

# inclination = 2
# RAAN = 3
# aop = argument of perigee = 5
# mean anomaly = 6
# mean motion = 7


def check_Path(downloadPath=downloadPath):   # dir 존재 유무 후 없을시 폴더 생성
    if os.path.isdir(downloadPath): pass
    else: os.makedirs(downloadPath)


def download_file(tle_list):
    options = Options()
    options.headless = False
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
        w = open(downloadPath+"\\TLE\\"+str(tle)+".txt", "w", encoding="utf8") # norad 번호 입력
        w.write(ret)
        w.close()

    time.sleep(1)
    print("파일 다운로드 완료\t ",dt.now())

def ex_tle(tle,index):
    if tle[0] == '2':
        return tle[index]

def ex_all_figure(norad,tle_name):
    filename = str(norad)
    r = open(downloadPath +"\\TLE\\" + filename + ".txt", "r", encoding="utf8")
    line = r.read().splitlines()
    temp = []

    for i in range(len(line)):
        temp.append(line[i].split())

    inclination = []
    RAAN = []
    aop = []
    mean_anomaly = []
    mean_motion = []

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
        # temp_c.append(abs(ret))
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

    # download_file(tle_list)

    for tle in tle_list:
        ex_all_figure(tle,tle_name)

    print("실행 완료")

    ##########
    # plt 그래프 사진 설정
    # 인클리네이션을 절대값으로 표기 vs 그대로 표기
