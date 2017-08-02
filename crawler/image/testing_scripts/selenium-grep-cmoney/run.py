#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement

# python lib
import sys
import json
import logging
import socket
import subprocess
import os
import time
import pprint
import datetime
from datetime import timedelta, date
import shutil
import uuid
import urllib2

# 3rd party lib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image


# logger
logging.basicConfig(level=logging.INFO, format='[CMO %(levelname).1s %(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# data
data = {'companies': [], 'date': '', 'date_tw': ''}


def grep_date():
    """
    Grep latest transaction date.
    :return:
    """
    while True:
        driver = webdriver.Firefox()
        try:
            driver.get('http://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html')
            time.sleep(20)

            # grep date
            d = driver.find_element(By.XPATH, '//*[@id="subtitle1"]').text.strip()
            ds = ['']
            for i in range(len(d)):
                if ord('0') <= ord(d[i]) <= ord('9'):
                    ds[-1] += d[i]
                else:
                    if ds[-1]:
                        ds.append('')
            data['date'] = '{}_{}_{}'.format(int(ds[0]) + 1911, ds[1], ds[2])
            data['date_tw'] = '{}_{}_{}'.format(ds[0], ds[1], ds[2])
            logging.info(data['date'])

            # check if today a transaction date
            if datetime.datetime.now().strftime('%Y_%m_%d') != data['date']:
                driver.quit()
                logging.info('{} 非交易日'.format(datetime.datetime.now().strftime('%Y_%m_%d')))
                sys.exit(0)
            # quit firefox
            driver.quit()
            break
        except WebDriverException:
            pass


def grep_image():
    # read companies
    companies = []
    data_dir = os.path.join('/data', data['date'])
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # tse
    with open(os.path.join(data_dir, 'tse.csv'), 'r') as f:
        lines = f.readlines()
        for line in lines:
            companies.append(line.split(',')[0].strip())
    # otc
    with open(os.path.join(data_dir, 'otc.csv'), 'r') as f:
        lines = f.readlines()
        for line in lines:
            companies.append(line.split(',')[0].strip())

    # Use firefox
    driver = webdriver.Firefox()
    i = 0
    while i < len(companies):
        if i % 50 == 0:
            driver.quit()
            driver = webdriver.Firefox()

        # company
        company = companies[i]
        # click to download file
        try:
            driver.get('http://www.cmoney.tw/notice/chart/stockchart.aspx?action=r&id={}&view=1'.format(company))

            # wait until charts be drawn
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'highcharts-tracker'))
            )

            # grep all brokers
            ele = driver.find_element(By.XPATH, '//*[@id="container"]')
            points = ele.location
            sz = ele.size

            # Save entire snapshot
            driver.save_screenshot('snapshot.png')

            # Crop the snapshot
            img = Image.open('snapshot.png')
            img = img.crop((points['x'], points['y'], points['x'] + sz['width'], points['y'] + sz['height']))
            img.save(os.path.join(data_dir, '{}.png'.format(company)))

            logging.info(u'{} 儲存走勢圖'.format(company))
            i += 1
        except NoSuchElementException:
            # logging.warning('{} 圖片沒找到'.format(company))
            pass
        except TimeoutException:
            # logging.warning('{} 逾時'.format(company))
            pass
        except WebDriverException as e:
            # logging.warning(e)
            # logging.warning('{} 重啟Firefox'.format(company))
            driver = webdriver.Firefox()
    # quit
    driver.quit()


def check():
    """
    Check if missing reports.
    :return:
    """
    # check all download files and convert to UTF-8
    cnt = 0
    data_dir = os.path.join('/data', data['date'])
    for company in data['companies']:
        png = os.path.join(data_dir, '{}.png'.format(company))
        if not os.path.exists(png):
            cnt += 1
            logging.warning('{}.png 遺失'.format(company))
    logging.warning('{}個png 遺失'.format(cnt))


def main():
    grep_date()
    grep_image()
    check()


if __name__ == '__main__':
    main()

