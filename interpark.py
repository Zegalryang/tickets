from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import time
import os
import math

kFrameSeat = 'ifrmSeat'
kFrameSeatDetail = 'ifrmSeatDetail'
kFrameSeatView = 'ifrmSeatView'

kCoord = 'coord'
kWeight = 'weight'
kElement = 'element'

chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=ChromeService(executable_path='./chromedriver'), options=chrome_options)
#driver.implicitly_wait(time_to_wait=60)

def login(userId, userPwd):
    print(' * Login ')

    try:
        driver.get("https://tickets.interpark.com")
        driver.find_element(By.LINK_TEXT, "로그인").click()
        e = driver.find_element(By.ID, "userId")
        e.send_keys(userId)
        e = driver.find_element(By.ID, "userPwd")
        e.send_keys(userPwd)
        driver.find_element(By.ID, "btn_login").click()
    except Exception as e:
        print('🔥 error', e)
        return False

    messages = driver.find_elements(By.CLASS_NAME, 'message')
    if messages:
        print('🔥 Error: {}'.format(messages[0].text))
        return False

    return True

def showBooking(product):
    print(' * Show Booking List')

    driver.get("https://tickets.interpark.com/goods/{}".format(product))

    print(" * Page title: {driver.title}")

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

    targetMonth = '8'
    targetMonth = targetMonth.zfill(2)

    e = driver.find_element(By.XPATH, '//*[@id="productSide"]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[1]/li[2]')
    print(' * 날짜(년/월): {}'.format(e.text))
    print(f' * 원하는 달: {targetMonth}')

    month = e.text.split(' ')[1]
    while month < targetMonth:
        btnNext = driver.find_element(By.XPATH, '//*[@id="productSide"]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[1]/li[3]')

        if not btnNext: break
        btnNext.click()

        print(' * 날짜 이동 (년/월): {}'.format(e.text))
        month = e.text.split(' ')[1]

    start = time.time()

    targetDate = '10'
    availableDates = driver.find_elements(By.XPATH, '//*[@id="productSide"]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[3]/li')
    selectedDate = None
    print(' * 예약 가능한 날짜')
    for i, d in enumerate(availableDates):
        try:
            state = d.get_attribute('class')
            print('  - {}: {}, {}'.format(i, d.text, state))

            if targetDate == d.text:
                selectedDate = d
                break

            if state == 'picked' or state == '': selectedDate = d
        except Exception as e:
            pass

    print('>>> Elapsed time of getting 예약가능 날짜: {}'.format(time.time() - start))
    if not selectedDate:
        print(' ??? No date exists')

    selectedDate.click()

    seq = "2회"
    seqItem = None
    e = driver.find_elements(By.CLASS_NAME, "timeTableLabel")
    print(' * 회차 테이블: {}'.format(e))
    for i, item in enumerate(e):
        if seq in item.text: seqItem = item
        print(' * {} 회차 {}: {}'.format(i+1, item.text, item.get_attribute('data-seq')))

    print(' * 선택: {}'.format(seqItem.text))
    seqItem.click()

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

lastFrame = None
def switchFrame(name, byType=By.ID, upToParent=True):
    global lastFrame

    # TODO: Find_Element가 나타날 때 가지 기다리는 루틴 추가
    print(' * switch frame: {}, type: {}, upToParent: {}, isSameFrame: {}'.format(name, byType, upToParent, lastFrame == name))

    if type(name) is str:
        name = [name]

    if lastFrame == name[-1]: return
    lastFrame = name[-1]

    if upToParent: driver.switch_to.default_content()
    for frame in name:
        driver.switch_to.frame(driver.find_element(byType, frame))

def waitingSlideCapcha(sleepDelay = 0.3):
    print(' * Slide Capcha 확인')

    appearedSlideCapcha = False

    while True:
        capcha = driver.find_elements(By.CLASS_NAME, 'captchSliderLayer')

        if not capcha: break
        if capcha[0].get_attribute('style') == 'display: none;': break

        print(' * Waiting slide capcha')
        appearedSlideCapcha = True
        time.sleep(0.3)

    if appearedSlideCapcha:
        sleepDelay += (sleepDelay * 0.3)
        if sleepDelay > 3.0: sleepDelay = 3

    print(' * Slide Capcha {} / {}'.format(appearedSlideCapcha, sleepDelay))
    return appearedSlideCapcha, sleepDelay

def waitUserQueue():
    while True:
        waiting = len(driver.find_elements(By.CLASS_NAME, "ticketWaiting"))
        if waiting == 0: break

        print(' * 사용자 큐 대기 상태')
        time.sleep(0.3)

def waitNoticeDialog():
    while True:
        closeBtn = driver.find_elements(By.CLASS_NAME, 'closeBtn')
        if not len(closeBtn): break

        print(' * 공지사항 제거...')
        for btn in closeBtn:
            btn.click()

        break

def waitPopupDialog():
    while True:
        closeBtn = driver.find_elements(By.CLASS_NAME, 'popupCloseBtn')
        if not len(closeBtn): break

        print(' * 팝업창 제거...')
        for btn in closeBtn:
            btn.click()

        break

def waitImageCapcha():
    focusText = False
    while True:
        isExists = len(driver.find_elements(By.ID, 'divRecaptcha'))
        if not isExists: break

        if not focusText:
            focusText = True
            driver.find_element(By.CLASS_NAME, 'validationTxt').click()

        # When hide set this 'display: none;'
        if driver.find_element(By.ID, 'divRecaptcha').get_attribute('style') != '': break

        print(' * Capcha 입력 대기...')
        time.sleep(0.3)

def getSections():
    print(' * getSections')
    sections = driver.find_elements(By.CLASS_NAME, 'kcl-user-action')
    return sections

def calculateDistance(sections, onlySections=False):
    assert sections, 'Section은 반드시 채워져야 한다'

    if onlySections: return [{kElement:s} for s in sections], None

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
            kElement: s,
            kCoord: [c0, c1],
            'name': name,
        }

        areas.append(area)

    print('>>> Elapsed time of getting area: {}'.format(time.time() - start))
    start = time.time()

    xMid = xAxis[0]/2 + xAxis[1]/2
    sideWeight = [0, 0]
    for area in areas:
        area[kWeight] = math.sqrt(abs(xMid - area[kCoord][0]) ** 2 + abs(area[kCoord][1]) ** 2)
        area['sideWeight'] = math.sqrt(abs(xMid - area[kCoord][0]) ** 2)
        sideWeight[0] = min(sideWeight[0], area['sideWeight'])
        sideWeight[1] = max(sideWeight[1], area['sideWeight'])

    xSideWeight = ((sideWeight[0] + sideWeight[1]) / 4) / 2

    areas = sorted(areas, key=lambda d: d[kWeight])

    print('>>> Elapsed time of calc weight of area: {}'.format(time.time() - start))

    # print (' * Sorted Areas: ')
    # for i in areas:
    #     print(' -', i)

    return areas, xSideWeight

def searchSeat(weight, sortGoodSeat = False):
    print(' * 좌석 선택')

    switchFrame(name=kFrameSeat)
    waitingSlideCapcha(0.5)
    switchFrame(name=kFrameSeatDetail, upToParent=False)

    while True:
        if len(driver.find_elements(By.ID, 'divSeatBox')) > 0: break
        print(' * 좌석 정보 기다리는중...')
        time.sleep(0.3)

    print(' * 좌석 정보 로드')
    seatBox = driver.find_element(By.ID, 'divSeatBox')

    if not sortGoodSeat:
        return [{kElement: seat} for seat in seatBox.find_elements(By.XPATH, './/span[starts-with(@class, "SeatN")]')]

    tmpSeats = []
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

        item = {kElement:seat, kCoord:coord[:]}
        seats.append(item)

    print('>>> Elapsed time of 좌석 좌표 계산: {}'.format(time.time() - start))
    print(' * seats count:', len(seats))

    if not seats: return False

    xMid = coord[0] / 2
    print(' * xMid {}'.format(xMid))
    # TODO: sideWeight 값이 완벽하지 않아 일단 막아둠
    # if a0['sideWeight'] < (xMid - weight): xMid = coord[0]
    # if a0['sideWeight'] > (xMid - weight): xMid = 0
    #print(' * coord: {} / sideweight: {} / xmid: {}'.format(coord, a0['sideWeight'], xMid))
    start = time.time()

    for seat in seats: seat[kWeight] = math.sqrt(abs(xMid - seat[kCoord][0]) ** 2 + abs(seat[kCoord][1]) ** 2)
    seats = sorted(seats, key=lambda d: d[kWeight])

    print('>>> Elapsed time of calc weight : {}'.format(time.time() - start))

    return seats

def selectSeats(ticketCount, seats):
    print(' * 좌석 정보')
    #for s in seats: print('   - ',s)
    for i in range(min(ticketCount, len(seats))):
        seat = seats[i]
        print('   - 좌석 선택: ', seat)
        seat[kElement].click()

hasSectionArea = False
def bookingSeatAreaType():
    global hasSectionArea

    print(' ### 영역으로 분리된 좌석')
    switchingAreaTimeDelay = 0.3
    selectedArea = 0
    areas = []

    while True:
        # 구역이 분리된 경우
        switchFrame(name=[kFrameSeat, kFrameSeatDetail])
        sections = getSections()

        if not sections: break
        hasSectionArea = True

        switchFrame(name=kFrameSeat)
        appearedSlideCapcha, switchingAreaTimeDelay = waitingSlideCapcha(switchingAreaTimeDelay)
        if appearedSlideCapcha: continue

        _, switchingAreaTimeDelay = waitingSlideCapcha(switchingAreaTimeDelay)

        switchFrame(name=kFrameSeatDetail, upToParent=False)
        areas, weight = calculateDistance(sections=sections)
        area = areas[selectedArea]
        if not area:
            print(' * Area를 찾을 수 없습니다.')
            break

        print(' * {} 영역 {} 입장, {}'.format(selectedArea, area[kElement].text, area))
        area[kElement].click()

        seats = searchSeat(weight=weight, sortGoodSeat=False)

        if seats:
            selectSeats(ticketCount=1, seats=seats)
            return True

        print(' * 다음 영역 이동')

        switchFrame(name=kFrameSeat)
        driver.find_element(By.CLASS_NAME, 'theater').click()

        time.sleep(switchingAreaTimeDelay)

        selectedArea += 1
        if selectedArea >= len(areas): selectedArea = 0

    return False

# --- main ------------------------------------
try:
    print('🏁 Start Booking Ticket')

    result = login(os.environ['TICKET_USERID'], os.environ['TICKET_USERPWD'])
    if not result:
        print('🔥 Login failure')
        exit(1)

    # showBooking('P0003831') # 영웅 # 바로좌석 + 위치선택
    # showBooking("24005595") # 이문세 # 바로 좌석
    # showBooking("24007162") # 변우석
    # showBooking('24007372') # 영역으로 분리됨
    showBooking('24006851')

    print(' * Check ticketWaiting')

    waitUserQueue()
    waitNoticeDialog()
    waitPopupDialog()

    switchFrame(name=kFrameSeat, upToParent=False)

    waitImageCapcha()

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

    print(' * 포도알 선택')

    foundSeat = False
    foundSeat = bookingSeatAreaType()

    if not foundSeat:
        print(' ### 객석이 바로 나오는 경우')
        ticketCount = 1
        hasSeatView = True

        # TODO: '🔥 객석이 나오는 경우가 아님'구현

        while hasSeatView:
            switchFrame(name=[kFrameSeat, kFrameSeatDetail])
            print(' * find seats')
            seats = driver.find_elements(By.CLASS_NAME, 'stySeat')
            print(' * found {} seats'.format(len(seats)))
            if seats:
                foundSeat = True
                for i in range(min(ticketCount, len(seats))):
                    print(' {} - {}'.format(i, seats[i]))
                    seats[i].click()

                break

            switchFrame(name=[kFrameSeat, kFrameSeatView])
            stages = driver.find_elements(By.CLASS_NAME, 'kcl-user-action')
            print(' * 선택가능 스테이지: {}'.format(len(stages) > 0))

            # 좌석만 있는 경우
            if not stages:
                driver.refresh()
                time.sleep(0.3)
                continue

            print(' - {}'.format(stages[-1].get_attribute('class')))
            stages[-1].click()
            time.sleep(3)

    if foundSeat:
        switchFrame(name=kFrameSeat)
        driver.find_element(By.CLASS_NAME, 'btnWrap').click() # 영역 나뉘는 경우, 스테이지 나뉘는 경우
        # driver.find_element(By.CLASS_NAME, 'kcl-user-action').click()

    while True: pass

finally:
    pass
    # 브라우저 닫기
    # driver.quit()
