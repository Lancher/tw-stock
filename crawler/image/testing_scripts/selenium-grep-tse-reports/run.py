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
import Queue
import urllib2
import signal
from urllib2 import HTTPError

# 3rd party lib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from PIL import Image


# logger
logging.basicConfig(level=logging.INFO, format='[TSE %(levelname).1s %(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# data
data = {'companies': [], 'date': ''}


def grep_date():
    """
    Grep latest transaction date.
    :return:
    """
    while True:
        driver = get_chrome_driver()
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
            logging.info(data['date'])

            # check if today a transaction date
            if datetime.datetime.now().strftime('%Y_%m_%d') != data['date']:
                driver.quit()
                logging.info('{} 非交易日'.format(datetime.datetime.now().strftime('%Y_%m_%d')))
                sys.exit(0)
            # quit chrome
            driver.quit()
            break
        except WebDriverException:
            pass


def get_firefox_driver():
    """
    Create a firefox with downloading settings.
    :return:
    """
    # data dir
    data_dir = os.path.join('/data', data['date'])
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    # set profile
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.manager.closeWhenDone", True)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.manager.focusWhenStarting", False)
    profile.set_preference("browser.download.manager.useWindow", False)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
    profile.set_preference("browser.helperApps.neverAsk.openFile", "text/csv,application/csv,application/octet-stream")
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv,application/csv,application/octet-stream")
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.dir", data_dir)
    # Use firefox
    driver = webdriver.Firefox(profile)
    return driver


def get_chrome_driver():
    """
    Create a chrome with downloading settings.
    :return:
    """
    # data dir
    data_dir = os.path.join('/data', data['date'])
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": data_dir}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(chrome_options=options)
    return driver


def grep_price():
    """
    Grep today's price report.
    :return:
    """
    while True:
        driver = get_chrome_driver()
        try:
            driver.get('http://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html')
            time.sleep(10)

            # select stock prices
            select = Select(driver.find_element(By.XPATH, '//*[@id="main-form"]/div/div/form/select'))
            select.select_by_value('ALLBUT0999')

            # search
            driver.find_element(By.XPATH, '//*[@id="main-form"]/div/div/form/a').click()
            time.sleep(10)

            # download
            driver.find_element(By.XPATH, '//*[@id="reports"]/div[1]/a[2]').click()
            time.sleep(5)
            logging.info('tse 下載今日開收報表')
            driver.quit()
            break
        except WebDriverException:
            pass

    # convert to UTF-8
    data_dir = os.path.join('/data', data['date'])
    mi_index = os.path.join(data_dir, 'MI_INDEX.csv')
    tse = os.path.join(data_dir, 'tse.csv')
    subprocess.check_output('iconv -f BIG-5 -t UTF-8 {} > {}'.format(mi_index, tse), shell=True)
    os.remove(mi_index)

    # parse file
    with open(tse, 'r') as f:
        lines = f.readlines()
    for line in lines:
        double_quote_cnt = 0
        company = []
        entry = ''
        for i in range(len(line)):
            if line[i] == '"':
                double_quote_cnt += 1
            elif line[i] == ',':
                if double_quote_cnt % 2 == 0:
                    company.append(entry.strip())
                    entry = ''
            else:
                entry += line[i]
        if company and len(company[0]) == 4 and len(company) >= 9:
            data['companies'].append(company[:9])

    # write to new file
    with open(tse, 'w') as f:
        for company in data['companies']:
            f.write('{}\n'.format(','.join(company)))
    logging.info('save {} tse companies'.format(len(data['companies'])))


def grep_report():
    q = Queue.Queue()
    for company in data['companies']:
        q.put(company[0])
    retry = {}

    # captchar daemon
    start_captchar_daemon()

    i = 0
    driver = get_chrome_driver()
    while not q.empty():
        # download reports
        sz = q.qsize()
        for _ in range(sz):
            company = q.get()
            # restart chrome every 50 times
            i += 1
            if i % 50 == 0:
                driver.quit()
                driver = get_chrome_driver()
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
                img.save('snapshot.png')
                img_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'snapshot.png')

                # get captchar
                response = urllib2.urlopen('http://127.0.0.1:8888/?f={}'.format(img_path))
                output = response.read()

                # set stock & captchar value
                driver.find_element(By.XPATH, '//*[@id="TextBox_Stkno"]').send_keys(str(company).strip())
                driver.find_element(By.XPATH, '//*[@id="Panel_bshtm"]/table/tbody/tr/td/table/tbody/tr[1]/td/div/div[2]/input').send_keys(output.strip())

                # submit
                driver.find_element(By.XPATH, '//*[@id="btnOK"]').click()

                # click to download file
                time.sleep(1)
                driver.find_element(By.XPATH, '//*[@id="HyperLink_DownloadCSV"]').click()
                time.sleep(1)
                logging.info('{} 下載成功'.format(company))
            except NoSuchElementException:
                try:
                    if u'查無資料' in driver.page_source:
                        pass
                    elif u'伺服器錯誤' in driver.page_source:
                        time.sleep(10)
                    elif u'驗證碼錯誤!' in driver.page_source:
                        pass
                    else:
                        pass
                except WebDriverException:
                    driver = get_chrome_driver()
            except WebDriverException:
                driver = get_chrome_driver()
            except HTTPError:
                start_captchar_daemon()

        # check all download files and convert to UTF-8
        cnt = 0
        data_dir = os.path.join('/data', data['date'])
        for company in data['companies']:
            if int(company[2]) != 0:
                csv = os.path.join(data_dir, '{}.csv'.format(company[0]))
                csv_utf8 = os.path.join(data_dir, '{}_{}.csv'.format(company[0], data['date']))
                if os.path.exists(csv):
                    subprocess.check_output('iconv -f BIG-5 -t UTF-8 {} > {}'.format(csv, csv_utf8), shell=True)
                    os.remove(csv)
                elif os.path.exists(csv_utf8):
                    pass
                else:
                    if company[0] not in retry:
                        retry[company[0]] = 0
                    if retry[company[0]] < 30:
                        retry[company[0]] += 1
                        cnt += 1
                        q.put(company[0])
                    else:
                        logging.warning('{}.csv 無法下載'.format(company[0]))
        logging.warning('{}個csv 遺失'.format(cnt))

    # quit chrome
    driver.quit()


def start_captchar_daemon():
    # kill old process
    try:
        if 'pid' in data:
            os.kill(data['pid'], signal.SIGTERM)
    except OSError:
        logging.warning('not such daemon {}'.format(data['pid']))

    # start new process
    script = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'captchar_recognize_daemon.py')
    cmd = [script]
    with open('/dev/null', 'w') as f:
        process = subprocess.Popen(cmd, stdout=f, stderr=f)
    data['pid'] = process.pid

    logging.info('captchar daemon {}'.format(process.pid))
    time.sleep(5)


def main():
    grep_date()
    grep_price()
    grep_report()


if __name__ == '__main__':
    main()






