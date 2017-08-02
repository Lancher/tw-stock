#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement

# python lib
import uuid
import time
from datetime import datetime

# 3rd party lib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from PIL import Image

# Use firefox
driver = webdriver.Firefox()

for _ in range(200):

    try:
        driver.get("http://bsr.twse.com.tw/bshtm/")

        # get into iframe
        driver.switch_to.frame(driver.find_element(By.ID, 'page1'))

        # Find captchar
        ele = driver.find_element(By.XPATH, '//*[@id="Panel_bshtm"]/table/tbody/tr/td/table/tbody/tr[1]/td/div/div[1]/img')
        points = ele.location
        sz = ele.size

        # Save entire snapshot
        driver.save_screenshot('snapshot.png')

        # Crop the snapshot
        img = Image.open('snapshot.png')
        img = img.crop((points['x'], points['y'], points['x'] + sz['width'], points['y'] + sz['height']))
        img.save('{}.png'.format(uuid.uuid4()))
        
        time.sleep(1)
        # get out of iframe
        # driver.switch_to.default_content()
    except WebDriverException as e:
        print(e)

# quit firefox
driver.quit()

