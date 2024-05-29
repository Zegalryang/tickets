from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import time
import os
import math

kFrameSeat = 'ifrmSeat'
kFrameSeatDetail = 'ifrmSeatDetail'

chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=ChromeService(executable_path='./chromedriver'), options=chrome_options)
#driver.implicitly_wait(time_to_wait=60)

def login(userId, userPwd):
    try:
        driver.get("https://tickets.interpark.com")
        driver.find_element(By.LINK_TEXT, "로그인").click()
        e = driver.find_element(By.ID, "userId")
        e.send_keys(userId)
        e = driver.find_element(By.ID, "userPwd")
        e.send_keys(userPwd)
        driver.find_element(By.ID, "btn_login").click()
    except Exception as e:
        return False

    return True

def showBooking(product):
    driver.get("https://tickets.interpark.com/goods/{}".format(product))

    print(f" * Page title: {driver.title}")

    try:
        element = driver.find_element(By.CLASS_NAME, "popupCloseBtn")
        element.click()
    except Exception as e:
        pass

    while True:
        e = len(driver.find_elements(By.LINK_TEXT, "예매하기"))
        print(' * 애매하기 존재 여부: {}'.format(e))
        if e: break
        time.sleep(0.3)

    # TODO: 월이 안맞는 경우 month prev / month next로 맞춰야 함.
    e = driver.find_element(By.XPATH, '//*[@id="productSide"]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[1]/li[2]')
    print(' * 날짜(년/월): {}'.format(e.text))

    start = time.time()

    print(' * 예약 가능한 날짜')
    for i in range(0, 30):
        try:
            e = driver.find_element(By.XPATH, '//*[@id="productSide"]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[3]/li[{}]'.format(i))
            print('  - {}, {}'.format(e.text, e.get_attribute('class')))
        except Exception as e:
            pass

    print(' >>> Elapsed time of getting 예약가능 날짜: {}'.format(time.time() - start))

    e = driver.find_element(By.XPATH, '//*[@id="productSide"]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[3]/li[{}]'.format('8'))
    e.click()

    e = driver.find_elements(By.CLASS_NAME, "timeTableLabel")
    print(' * 회차 테이블: {}'.format(e))
    for i, item in enumerate(e):
        print(' * {} 회차 {}: {}'.format(i+1, item.text, item.get_attribute('data-seq')))

    print(' * before window_handles: ', driver.window_handles)
    driver.find_element(By.LINK_TEXT, "예매하기").click()

    while True:
        if len(driver.window_handles) >= 2: break
        print(' * 예약 창 기다리는중...-')
        time.sleep(0.3)

    print(' * after window_handles: ', driver.window_handles)
    print(' * 포도알 화면 진입')
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(1)
    print(' * switch driver title: {}'.format(driver.title))

def switchFrame(name, byType=By.ID, upToParent=True):
    if upToParent: driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(byType, name))

def arrangeAreaType(ticketCount=1):
    sections = driver.find_elements(By.CLASS_NAME, 'kcl-user-action')
    if not sections: return

    xAxis = [0, 0]
    yAxis = [0, 0]

    start = time.time()

    areas = []
    for s in sections:
        name = s.get_attribute('onmouseover').split("'")[1]
        coords = s.get_attribute('coords').split(',')

        c0 = int(coords[0])
        c1 = int(coords[1])
        xAxis[0] = min(xAxis[0], c0)
        xAxis[1] = max(xAxis[1], c0)
        yAxis[0] = min(yAxis[0], c1)
        yAxis[1] = max(yAxis[1], c1)

        area = {
            'element': s,
            'coord': [c0, c1],
            'name': name,
        }

        areas.append(area)

    print(' >>> Elapsed time of getting area: {}'.format(time.time() - start))
    start = time.time()

    xMid = xAxis[0]/2 + xAxis[1]/2
    sideWeight = [0, 0]
    for area in areas:
        area['weight'] = math.sqrt(abs(xMid - area['coord'][0]) ** 2 + abs(area['coord'][1]) ** 2)
        area['sideWeight'] = math.sqrt(abs(xMid - area['coord'][0]) ** 2)
        sideWeight[0] = min(sideWeight[0], area['sideWeight'])
        sideWeight[1] = max(sideWeight[1], area['sideWeight'])

    xSideWeight = ((sideWeight[0] + sideWeight[1]) / 4) / 2

    areas = sorted(areas, key=lambda d: d['weight'])

    print(' >>> Elapsed time of calc weight of area: {}'.format(time.time() - start))

    print (' * Sorted Areas: ')
    for i in areas:
        print(' -', i)

    a0 = areas[0]
    centerPosition = 0
    if a0['sideWeight'] < (xMid - xSideWeight): centerPosition = -1
    if a0['sideWeight'] > (xMid - xSideWeight): centerPosition = 1

    print(' * 영역 {} 입장'.format(a0['element'].text))

    a0['element'].click()

    while True:
        if len(driver.find_elements(By.ID, 'divSeatBox')) > 0: break
        print(' * 좌석 정보 기다리는중...')
        time.sleep(0.3)

    print(' * 좌석 정보 로드')
    seatBox = driver.find_element(By.ID, 'divSeatBox')
    tmpSeats = seatBox.find_elements(By.XPATH, './/span[starts-with(@class, "Seat")]')

    start = time.time()

    coord = [0, 0]
    seats = []
    for seat in tmpSeats:
        className = seat.get_attribute('class')

        if className == 'SeatT':
            coord[0] = 0
            coord[1] += 1
            continue

        coord[0] += 1
        if className == 'SeatB':continue
        if seat.get_attribute('id') == '':continue

        item = {'element':seat, 'coord':coord[:]}
        seats.append(item)

    print(' >>> Elapsed time of 좌석 좌표 계산: {}'.format(time.time() - start))

    xMid = coord[0] / 2
    if centerPosition == -1: xMid = coord[0]
    if centerPosition == 1: xMid = 0

    start = time.time()

    for seat in seats: seat['weight'] = math.sqrt(abs(xMid - seat['coord'][0]) ** 2 + abs(seat['coord'][1]) ** 2)
    seats = sorted(seats, key=lambda d: d['weight'])

    print(' >>> Elapsed time of calc weight : {}'.format(time.time() - start))

    for i in range(ticketCount):
        seats[i]['element'].click()

    switchFrame(name=kFrameSeat)
    driver.find_element(By.CLASS_NAME, 'btnWrap').click()

try:
    result = login(os.environ['TICKET_USERID'], os.environ['TICKET_USERPWD'])
    if not result:
        print(' * Login failure')
        exit(1)

    showBooking('24007372')#("24007162")
    print(' * Check ticketWaiting')

    while True:
        waiting = len(driver.find_elements(By.CLASS_NAME, "ticketWaiting"))
        print(' * 사용자 큐 대기 상태 - waiting')
        if waiting == 0: break

        print(' * 사용자 큐 대기 상태')
        time.sleep(0.3)

    switchFrame(name=kFrameSeat, upToParent=False)

    btnBackToAllSeats = driver.find_element(By.CLASS_NAME, 'theater')
    btnNext = driver.find_element(By.CLASS_NAME, 'btnWrap')
    tmpGrades = driver.find_elements(By.ID, 'GradeRow')

    grades = []
    print(' * 좌석등급')
    for g in tmpGrades:
        text = g.text
        print(' - {}'.format(text))
        if '0석' in text:
            print('     0석 제거')
            continue

        grades.append(g)

    print('*' * 10)
    for g in grades:
        print(' -', g.text)

    focusText = False
    while True:
        isExists = len(driver.find_elements(By.ID, 'divRecaptcha'))
        if not isExists: break

        if not focusText:
            focusText = True
            driver.find_element(By.CLASS_NAME, 'validationTxt').click()

        # When hide set this 'display: none;'
        if driver.find_element(By.ID, 'divRecaptcha').get_attribute('style') != '': break #

        print(' * Capcha 입력 대기...')
        time.sleep(0.3)

    print(' * 포도알 선택')
    switchFrame(name=kFrameSeatDetail, upToParent=False)

    # 구역이 분리된 경우
    arrangeAreaType(3)

    # frame = driver.find_element(By.ID, 'ifrmSeat')
    # driver.switch_to.frame(frame)

    # btnBackToAllSeats = driver.find_element(By.CLASS_NAME, 'theater')
    # btnNext = driver.find_element(By.CLASS_NAME, 'btnWrap')
    # btnNext.click()

    # TODO: 좌석이 없으면 다른곳에서 선택
    # TODO: 좌석이 있으면 선택

    # 이전화면 CLASS_NAME='theater'
    # 몇 초간 대기 (테스트 목적으로)
    # while True: pass

finally:
    pass
    # 브라우저 닫기
    # driver.quit()