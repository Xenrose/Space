# 사용한 모듈
# 내장 - re, datetime, os
# pip - requests, beautifulsoup4, lxml *중요


import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime as dt
import os


working_dir = "C:\\Users\\{}\\Desktop\\Space\\Web_Crawling".format(os.getlogin())

All_nation_url = []                 # 크롤링 시 사용할 전역변수 / 전 국가의 url 수집
Each_nation_url = []                # 크롤링 시 사용할 전역변수 / 수집한 국가 url에서 목적별 url 수집
Sat_url = []                        # 크롤링 시 사용할 전역변수 / 개별 위성 url 수집

First_url = "https://space.skyrocket.de/directories/sat_c.htm"      # 크롤링 시작 url


today_str = str(dt.now().year) + '{:0>2}'.format(str(dt.now().month)) + '{:0>2}'.format(str(dt.now().day)) 

# 개별 위성에 대한 url 수집 list
# 프로그램이 종료되기 전까지 도중에 실행 불가능
url_list = today_str + "_url_list.csv"
f_url = open(working_dir + "/" + url_list, "w", encoding="utf-8-sig")
f_url.close()
f_url = open(url_list, "a", encoding="utf-8-sig")


# 개별 위성에 대한 data form 생성
# 프로그램이 종료되기 전까지 도중에 실행 불가능
sat_data = today_str + "_sat_data.csv"
f_data = open(working_dir + "/" + sat_data, "w", encoding="utf-8-sig")
f_data.write("COSPAR,SAT NAME,NATION,TYPE,OPERATOR,EQUIPMENT,LIFETIE,MASS,LAUNCH SITE,LAUNCH DATE,LAUNCH VEHICLE"); f_data.write("\n")
f_data.close()
f_data = open(sat_data, "a", encoding="utf-8-sig")


def check_Path(working_dir=working_dir):   # dir 존재 유무 후 없을시 폴더 생성
    if os.path.isdir(working_dir): pass
    else: os.makedirs(working_dir)


def line_del(str):                         # 수집한 크롤링 데이터에서 불필요한 부분을 삭제해주는 함수
    if "\n" in str:
        str = str.split("\n")
        str = str[0].strip() + " " + str[1].strip()
    return str


def extract_url(url, list, sat):           # url 변수를 입력받고 해당 url에 대한 파싱 및 href만 추출하는 함수
    res = requests.get(url)                # 파라미터
    res.raise_for_status()                 # 1. 파싱할 url / href를 추출해 저장할 list / href 추출시 url 에 포함된 공통 키워드
    soup = BeautifulSoup(res.text, "lxml")

    table = soup.find_all("li")

    for real in table:
        try:
            if re.search(str(sat),real.a["href"]) and real.a["href"] not in list:
                list.append(real.a["href"])
            else:
                continue
        except:
            continue


def extract_sat_data(url):                 # 파라미터로 url을 받고 해당 url에서 실질적으로 crawling을 진행하는 함수
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")

    # crawling 하는 data list

    # SATname / Nation / Type / Operator / Equipment / Lifetime / Mass
    nation = line_del(soup.find("td",attrs={"id":"sdnat"}).get_text().replace(","," /"))
    Type = line_del(soup.find("td",attrs={"id":"sdtyp"}).get_text().replace(","," /"))
    Operator = line_del(soup.find("td",attrs={"id":"sdope"}).get_text().replace(","," /"))
    Equipment = line_del(soup.find("td",attrs={"id":"sdequ"}).get_text().replace(","," /"))
    Lifetime = line_del(soup.find("td",attrs={"id":"sdlif"}).get_text().replace(","," /"))
    Mass = line_del(soup.find("td",attrs={"id":"sdmas"}).get_text().replace(","," /"))

    # 0 sat name / 1 cospar / 2 date / 3 LS / 4 "" / 5 Launch vehicle / 6 Remarks // 7 new line
    ano_sat = soup.find("table",attrs={"id":"satlist"}).find_all("td")
    
    # last form
    # 1 cospa / 0 satname / nation / Type / Operator / Equipment / Lifetime / Mass / launch_site / launch_date / launch_vehicle
    for z in range(0,len(ano_sat)//7):
        cospa = line_del(ano_sat[1+(z*7)].get_text().replace(","," /"))
        if len(cospa) < 5:
            cospa = "-"
        if "/td" in cospa:
            cospa = "*-"
        satname_sub = line_del(ano_sat[0+(z*7)].get_text().replace(","," /"))
        launch_site = line_del(ano_sat[3+(z*7)].get_text().replace(","," /"))
        launch_date = line_del(ano_sat[2+(z*7)].get_text().replace(","," /"))
        launch_vehicle = line_del(ano_sat[5+(z*7)].get_text().replace(","," /"))
        f_data.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}".format(cospa,satname_sub,nation,Type,Operator,Equipment,Lifetime,Mass,launch_site,launch_date,launch_vehicle)); f_data.write("\n")


if __name__ == "__main__":          # 메인 함수
    start_time = dt.today()         # 총 실행시간을 알기 위한 시작시간 변수
    check_Path()                    # check_working_dir
    
    extract_url(First_url, All_nation_url, "sat_c")
    print("All_nation_url 완료")    

    for z in All_nation_url:
        extract_url("https://space.skyrocket.de/directories/"+z, Each_nation_url, "sat_")
    
    print("Each_nation_url 완료")

    
    for j in Each_nation_url:
        extract_url("https://space.skyrocket.de/directories/"+j,Sat_url, "doc_sdat")
    
    print("Sat_url 완료")

    # Sat_url에는 중복값이 있으므로 중복값을 제거해준 뒤 계속 진행 
    # extract_url함수에서 이미 url 중복 패스 처리를 하기 때문에 필요 없는 부분
    # Sat_url = list(set(Sat_url))

    for x in Sat_url:
        f_url.write(x.replace("..","https://space.skyrocket.de")); f_url.write("\n")

    f_url.close()
    print("url 수집 완료")


    print("extract_sat_data 시작")
    count = 0
    for idx, y in enumerate(Sat_url):
        try:
            extract_sat_data(str(y.replace("..","https://space.skyrocket.de")))
        except:
            count +=1
            pass
        for z in range(10,100,10):
            if ((idx/len(Sat_url))*100)>=z and (((idx-1)/len(Sat_url))*100)<z:
                print("{0}퍼센트 완료".format(z))

    f_data.close()    
    end_time = dt.today()
    print("Data 추출 완료.")
    print("{0}개의 url에서 데이터를 수집했으며 이 중 오류 발생 url {1}건".format(len(Sat_url), count))
    print("소요 시간: {0}".format(end_time-start_time))