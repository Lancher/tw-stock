from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image

# Use firefox
driver = webdriver.Firefox()

for _ in range(200):
    driver.get("http://www.tpex.org.tw/web/stock/aftertrading/broker_trading/brokerBS.php")

    # Find captchar
    ele = driver.find_element(By.XPATH, '/html/body/center/div[3]/div[2]/div[4]/form/div[3]/div/img')
    points = ele.location
    sz = ele.size

    # Save entire snapshot
    driver.save_screenshot('snapshot.png')

    # Crop the snapshot
    img = Image.open('snapshot.png')
    img = img.crop((points['x'], points['y'], points['x'] + sz['width'], points['y'] + sz['height']))
    img.save('chars_{}.png'.format(datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M-%S')))

# quit firefox
driver.quit()

