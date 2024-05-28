from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import time
import os

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

    print(' * 예약 가능한 날짜')
    for i in range(0, 30):
        try:
            e = driver.find_element(By.XPATH, '//*[@id="productSide"]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[3]/li[{}]'.format(i))
            print('  - {}, {}'.format(e.text, e.get_attribute('class')))
        except Exception as e:
            pass

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

    print(' * 포도알 화면 진입')
    driver.switch_to.window(driver.window_handles[1])
    print(' * switch driver title: {}'.format(driver.title))

try:
    result = login(os.environ['TICKET_USERID'], os.environ['TICKET_USERPWD'])
    if not result:
        print(' * Login failure')
        exit(1)

    showBooking("24007162")

    while True:
        waiting = len(driver.find_elements(By.CLASS_NAME, "ticketWaiting"))
        if waiting == 0: break

        print(' * 사용자 큐 대기 상태')
        time.sleep(0.3)

    frame = driver.find_element(By.ID, 'ifrmSeat')
    driver.switch_to.frame(frame)

    while True:
        isExists = len(driver.find_elements(By.ID, 'divRecaptcha'))
        if not isExists: break

        # When hide set this 'display: none;'
        if driver.find_element(By.ID, 'divRecaptcha').get_attribute('style') != '': break #

        print(' * Capcha 입력 대기...')
        time.sleep(0.3)

    print(' * 포도알 선택')
    frame = driver.find_element(By.ID, 'ifrmSeatDetail')
    driver.switch_to.frame(frame)

    sections = driver.find_elements(By.CLASS_NAME, 'kcl-user-action')
    xAxis = [0, 0]
    yAxis = [0, 0]

    areas = []
    for s in sections:
        name = s.get_attribute('onmouseover').split("'")[1]
        coords = s.get_attribute('coords').split(',')

        for c in coords:
            xAxis[0] = min(xAxis[0], c[0])
            xAxis[1] = max(xAxis[1], c[0])
            yAxis[0] = min(yAxis[0], c[1])
            yAxis[1] = max(yAxis[1], c[1])
        
        area = {
            'element': s,
            'coord': c[:1],
            'name': name
        }

        areas.append(area)

    # 몇 초간 대기 (테스트 목적으로)
    # while True: pass

finally:
    pass
    # 브라우저 닫기
    # driver.quit()