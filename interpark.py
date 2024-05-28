from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
#from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import os

# ChromeDriver를 자동으로 다운로드 및 설정
chrome_options = Options()
#chrome_options.add_argument("--ignore-certificate-errors")  # SSL 인증서 오류 무시
#chrome_options.add_argument("--disable-web-security")       # 웹 보안 비활성화
chrome_options.add_argument("--window-size=1920,1080")
#driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
driver = webdriver.Chrome(service=ChromeService(executable_path='./chromedriver'), options=chrome_options)
#driver.implicitly_wait(time_to_wait=60)


try:
    driver.get("https://tickets.interpark.com")
    driver.find_element(By.LINK_TEXT, "로그인").click()
    e = driver.find_element(By.ID, "userId")
    e.send_keys(os.environ['TICKET_USERID'])
    e = driver.find_element(By.ID, "userPwd")
    e.send_keys(os.environ['TICKET_USERPWD'])
    driver.find_element(By.ID, "btn_login").click()

    driver.get("https://tickets.interpark.com/goods/24007162")

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

    driver.find_element(By.LINK_TEXT, "예매하기").click()

    # 몇 초간 대기 (테스트 목적으로)
    time.sleep(5)

finally:
    # 브라우저 닫기
    driver.quit()