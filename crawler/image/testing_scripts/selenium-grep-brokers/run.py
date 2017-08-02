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
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from PIL import Image


# logger
logging.basicConfig(level=logging.INFO, format='[BRO %(levelname).1s %(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# data
data = {'brokers': [], 'date': '', 'date_tw': ''}


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


def grep_brokers():

    while True:
        # Use firefox
        driver = webdriver.Firefox()
        try:
            driver.get('http://www.twse.com.tw/zh/brokerService/brokerList')

            # sleep
            time.sleep(5)

            # select all brokers
            select = Select(driver.find_element(By.ID, 'maxLength'))
            select.select_by_value('-1')

            # sleep
            time.sleep(5)

            # grep all brokers
            ele = driver.find_element(By.XPATH, '//*[@id="main"]/main/article/table')
            html = ele.get_attribute('innerHTML')

            # parse html
            soup = BeautifulSoup(html.encode('utf-8'), 'html.parser')
            tbody = soup.find_all('tbody')
            trs = tbody[0].find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                data['brokers'].append((
                    tds[0].get_text(),
                    tds[1].get_text(),
                    tds[3].get_text()
                ))

            driver.get('http://www.twse.com.tw/brokerService/branchList')

            # sleep
            time.sleep(5)

            # select all brokers
            select = Select(driver.find_element(By.ID, 'maxLength'))
            select.select_by_value('-1')

            # sleep
            time.sleep(5)

            # grep all brokers
            ele = driver.find_element(By.XPATH, '//*[@id="main"]/main/article/table')
            html = ele.get_attribute('innerHTML')

            # parse html
            soup = BeautifulSoup(html.encode('utf-8'), 'html.parser')
            tbody = soup.find_all('tbody')
            trs = tbody[0].find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                data['brokers'].append((
                    tds[0].get_text(),
                    tds[1].get_text(),
                    tds[3].get_text()
                ))

            # save brokers
            data_dir = os.path.join('/data', data['date'])
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            with open(os.path.join(data_dir, 'brokers.csv'), 'w') as f:
                for broker in data['brokers']:
                    f.write('{}, {}, {}\n'.format(broker[0], broker[1].encode('utf-8'), broker[2].encode('utf-8')))

            logging.info('save {} brokers'.format(len(data['brokers'])))
            driver.quit()

            break
        except WebDriverException:
            data['brokers'] = []
            pass


def main():
    grep_date()
    grep_brokers()


if __name__ == '__main__':
    main()

