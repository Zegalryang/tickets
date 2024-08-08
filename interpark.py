from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import time
import os
import math
from product import info
from logger import logger

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
    try:
        driver.get("https://tickets.interpark.com")
        driver.find_element(By.LINK_TEXT, "로그인").click()
        e = driver.find_element(By.ID, "userId")
        e.send_keys(userId)
        e = driver.find_element(By.ID, "userPwd")
        e.send_keys(userPwd)
        driver.find_element(By.ID, "btn_login").click()
    except Exception as e:
        logger.debug(f'🔥 error {e}')
        return False

    messages = driver.find_elements(By.CLASS_NAME, 'message')
    if messages:
        logger.debug('🔥 Error: {}'.format(messages[0].text))
        return False

    return True

def showBooking(product, targetMonth="01", targetDay="01", seq='1회'):
    logger.info(' * Show Booking List')

    driver.get("https://tickets.interpark.com/goods/{}".format(product))

    logger.info(f" * Page title: {driver.title}")

    try:
        element = driver.find_element(By.CLASS_NAME, "popupCloseBtn")
        element.click()
    except Exception as e:
        pass

    while True:
        e = len(driver.find_elements(By.LINK_TEXT, "예매하기"))
        logger.debug(' * 애매하기 존재 여부: {}'.format(e))
        if e: break
        time.sleep(0.3)

    e = driver.find_element(By.XPATH, '//*[@id="productSide"]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[1]/li[2]')
    logger.debug(' * 날짜(년/월): {}'.format(e.text))
    logger.debug(f' * 원하는 달: {targetMonth}')

    month = e.text.split(' ')[1]
    while month < targetMonth:
        btnNext = driver.find_element(By.XPATH, '//*[@id="productSide"]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[1]/li[3]')

        if not btnNext: break
        btnNext.click()

        logger.debug(' * 날짜 이동 (년/월): {}'.format(e.text))
        month = e.text.split(' ')[1]

    start = time.time()

    availableDates = driver.find_elements(By.XPATH, '//*[@id="productSide"]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[3]/li')
    selectedDate = None
    logger.debug(' * 예약 가능한 날짜')
    for i, d in enumerate(availableDates):
        try:
            state = d.get_attribute('class')
            logger.debug('  - {}: {}, {}'.format(i, d.text, state))

            if targetDay == d.text:
                selectedDate = d
                break

            if state == 'picked' or state == '': selectedDate = d
        except Exception as e:
            pass

    logger.debug('>>> Elapsed time of getting 예약가능 날짜: {}'.format(time.time() - start))
    if not selectedDate:
        logger.debug(' ??? No date exists')

    selectedDate.click()

    seqItem = None
    e = driver.find_elements(By.CLASS_NAME, "timeTableLabel")
    logger.debug(' * 회차 테이블: {}'.format(e))
    for i, item in enumerate(e):
        if seq in item.text: seqItem = item
        logger.debug(' * {} 회차 {}: {}'.format(i+1, item.text, item.get_attribute('data-seq')))

    logger.debug(' * 선택: {}'.format(seqItem.text))
    if seqItem: seqItem.click()

    logger.debug(f' * before window_handles: {driver.window_handles}')
    driver.find_element(By.LINK_TEXT, "예매하기").click()

    while True:
        if len(driver.window_handles) >= 2: break
        logger.debug(' * 예약 창 기다리는중...-')
        time.sleep(0.3)

    logger.debug(f' * after window_handles: {driver.window_handles}')
    logger.debug(' * 포도알 화면 진입')
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(1)
    logger.debug(' * switch driver title: {}'.format(driver.title))

lastFrame = None
def switchFrame(name, byType=By.ID, upToParent=True):
    global lastFrame

    # TODO: Find_Element가 나타날 때 가지 기다리는 루틴 추가
    logger.debug(' * switch frame: {}, type: {}, upToParent: {}, isSameFrame: {}'.format(name, byType, upToParent, lastFrame == name))

    if type(name) is str:
        name = [name]

    if lastFrame == name[-1]: return
    lastFrame = name[-1]

    if upToParent: driver.switch_to.default_content()
    for frame in name:
        driver.switch_to.frame(driver.find_element(byType, frame))

def waitingSlideCapcha(sleepDelay = 0.3):
    logger.info(' * Slide Capcha 확인')

    appearedSlideCapcha = False

    while True:
        capcha = driver.find_elements(By.CLASS_NAME, 'captchSliderLayer')

        if not capcha: break
        if capcha[0].get_attribute('style') == 'display: none;': break

        logger.debug(' * Waiting slide capcha')
        appearedSlideCapcha = True
        time.sleep(0.3)

    if appearedSlideCapcha:
        sleepDelay += (sleepDelay * 0.3)
        if sleepDelay > 3.0: sleepDelay = 3

    logger.debug(' * Slide Capcha {} / {}'.format(appearedSlideCapcha, sleepDelay))
    return appearedSlideCapcha, sleepDelay

def waitUserQueue():
    while True:
        waiting = len(driver.find_elements(By.CLASS_NAME, "ticketWaiting"))
        if waiting == 0: break

        logger.debug(' * 사용자 큐 대기 상태')
        time.sleep(0.3)

def waitNoticeDialog():
    while True:
        closeBtn = driver.find_elements(By.CLASS_NAME, 'closeBtn')
        if not len(closeBtn): break

        logger.debug(' * 공지사항 제거...')
        for btn in closeBtn:
            btn.click()

        break

def waitPopupDialog():
    while True:
        closeBtn = driver.find_elements(By.CLASS_NAME, 'popupCloseBtn')
        if not len(closeBtn): break

        logger.debug(' * 팝업창 제거...')
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

        logger.debug(' * Capcha 입력 대기...')
        time.sleep(0.3)

def getSections():
    logger.debug(' * getSections')
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

    logger.debug('>>> Elapsed time of getting area: {}'.format(time.time() - start))
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

    logger.debug('>>> Elapsed time of calc weight of area: {}'.format(time.time() - start))

    # print (' * Sorted Areas: ')
    # for i in areas:
    #     logger.debug(' -', i)

    return areas, xSideWeight

def searchSeat(weight, sortGoodSeat = False):
    logger.info(' * 좌석 선택')

    switchFrame(name=kFrameSeat)
    waitingSlideCapcha(0.5)
    switchFrame(name=kFrameSeatDetail, upToParent=False)

    while True:
        if len(driver.find_elements(By.ID, 'divSeatBox')) > 0: break
        logger.debug(' * 좌석 정보 기다리는중...')
        time.sleep(0.3)

    logger.debug(' * 좌석 정보 로드')
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

    logger.debug('>>> Elapsed time of 좌석 좌표 계산: {}'.format(time.time() - start))
    logger.debug(' * seats count:', len(seats))

    if not seats: return False

    xMid = coord[0] / 2
    logger.debug(' * xMid {}'.format(xMid))
    # TODO: sideWeight 값이 완벽하지 않아 일단 막아둠
    # if a0['sideWeight'] < (xMid - weight): xMid = coord[0]
    # if a0['sideWeight'] > (xMid - weight): xMid = 0
    #logger.debug(' * coord: {} / sideweight: {} / xmid: {}'.format(coord, a0['sideWeight'], xMid))
    start = time.time()

    for seat in seats: seat[kWeight] = math.sqrt(abs(xMid - seat[kCoord][0]) ** 2 + abs(seat[kCoord][1]) ** 2)
    seats = sorted(seats, key=lambda d: d[kWeight])

    logger.debug('>>> Elapsed time of calc weight : {}'.format(time.time() - start))

    return seats

def selectSeats(ticketCount, seats):
    logger.debug(' * 좌석 정보')
    #for s in seats: logger.debug('   - ',s)
    for i in range(min(ticketCount, len(seats))):
        seat = seats[i]
        logger.debug('   - 좌석 선택: ', seat)
        seat[kElement].click()

hasSectionArea = False
def bookingSeatAreaType():
    global hasSectionArea

    logger.debug(' ### 영역으로 분리된 좌석')
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
            logger.debug(' * Area를 찾을 수 없습니다.')
            break

        logger.debug(' * {} 영역 {} 입장, {}'.format(selectedArea, area[kElement].text, area))
        area[kElement].click()

        seats = searchSeat(weight=weight, sortGoodSeat=False)

        if seats:
            selectSeats(ticketCount=1, seats=seats)
            return True

        logger.debug(' * 다음 영역 이동')

        switchFrame(name=kFrameSeat)
        driver.find_element(By.CLASS_NAME, 'theater').click()

        time.sleep(switchingAreaTimeDelay)

        selectedArea += 1
        if selectedArea >= len(areas): selectedArea = 0

    return False

# --- main ------------------------------------
try:
    logger.info('🏁 Start Booking Ticket')

    result = login(info.userId(), info.userPwd())
    if not result:
        logger.info('🔥 Login failure')
        exit(1)

    showBooking(
        product=info.productId(),
        targetMonth=info.month(),
        targetDay=info.day(),
        seq=info.seq())

    logger.info(' * Check ticketWaiting')

    waitUserQueue()
    waitNoticeDialog()
    waitPopupDialog()

    switchFrame(name=kFrameSeat, upToParent=False)

    waitImageCapcha()

    tmpGrades = driver.find_elements(By.ID, 'GradeRow')
    grades = []
    logger.debug(' * 좌석등급')
    for g in tmpGrades:
        text = g.text
        logger.debug(' - {}'.format(text))
        if '0석' in text:
            logger.debug('     0석 제거')
            continue

        grades.append(g)

    logger.debug('*' * 10)
    for g in grades:
        logger.debug(' -', g.text)

    logger.debug(' * 포도알 선택')

    foundSeat = False
    foundSeat = bookingSeatAreaType()

    if not foundSeat:
        logger.debug(' ### 객석이 바로 나오는 경우')
        ticketCount = 1
        hasSeatView = True

        # TODO: '🔥 객석이 나오는 경우가 아님'구현

        while hasSeatView:
            switchFrame(name=[kFrameSeat, kFrameSeatDetail])
            logger.debug(' * find seats')
            seats = driver.find_elements(By.CLASS_NAME, 'stySeat')
            logger.debug(' * found {} seats'.format(len(seats)))
            if seats:
                foundSeat = True
                for i in range(min(ticketCount, len(seats))):
                    logger.debug(' {} - {}'.format(i, seats[i]))
                    seats[i].click()

                break

            switchFrame(name=[kFrameSeat, kFrameSeatView])
            stages = driver.find_elements(By.CLASS_NAME, 'kcl-user-action')
            logger.debug(' * 선택가능 스테이지: {}'.format(len(stages) > 0))

            # 좌석만 있는 경우
            if not stages:
                driver.refresh()
                time.sleep(0.3)
                continue

            logger.debug(' - {}'.format(stages[-1].get_attribute('class')))
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
