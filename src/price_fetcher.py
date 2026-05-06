import time
from seleniumbase import Driver
import pyautogui

def get_prices(id):
    url = f"https://steamdb.info/app/{id}/"

    driver = Driver(uc_cdp=True, incognito=True)

    try:
        driver.get(url)

        driver.wait_for_element_present("div.highcharts-container", timeout=15)

        driver.execute_script("Highcharts.charts[0].downloadCSV();")

        time.sleep(2)

        pyautogui.press('Enter')
        time.sleep(1)

        print('Downloaded successfully')

    except:
        print('Request error')
    finally:    
        driver.quit()
        

test_id = 4000

get_prices(test_id)