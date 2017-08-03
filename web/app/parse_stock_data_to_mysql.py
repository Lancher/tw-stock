#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement

# python lib
import json
import logging
import socket
import subprocess
import os
import time
import pprint
from datetime import date, timedelta, datetime
from datetime import timedelta, date
import shutil
import uuid
import Queue
import urllib2
import argparse
import MySQLdb


logging.basicConfig(level=logging.INFO, format='[SQL %(levelname).1s %(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
data = {}


def parse(args):
    s = datetime.strptime(args.s, '%Y_%m_%d')
    e = datetime.strptime(args.e, '%Y_%m_%d')
    delta = e - s + timedelta(days=1)

    con = MySQLdb.connect(host='db', user='root', passwd='1234', db='stock')
    with con:
        cur = con.cursor()
        for i in range(delta.days):
            d = (s + timedelta(days=i)).strftime('%Y_%m_%d')
            brokers_csv = os.path.join(args.d, d, 'brokers.csv')
            tse_csv = os.path.join(args.d, d, 'tse.csv')
            otc_csv = os.path.join(args.d, d, 'otc.csv')
            if not os.path.exists(brokers_csv):
                continue

            # parse brokers
            brokers = []
            logging.info(brokers_csv)
            with open(brokers_csv) as f:
                for line in f:
                    code, name, addr = line.split(',', 2)
                    brokers.append((code.strip(), name.strip(), addr.strip()))

            # insert to table `broker` (code, name, address, focus)
            for broker in brokers:
                cur.execute("SELECT code FROM broker WHERE BINARY code='{}' "
                            .format(broker[0]))
                res = cur.fetchall()
                if not res:
                    cur.execute("INSERT INTO broker (code, name, address, focus) VALUES ('{}', '{}', '{}', {}) "
                                .format(broker[0], broker[1], broker[2], 0))

            # parse tse companies
            # 0        1        2        3        4        5      6      7      8      9
            # 證券代號, 證券名稱, 成交股數, 成交筆數, 成交金額, 開盤價, 最高價, 最低價, 收盤價, 漲跌(+/-)
            # code     name     amount            price   open    high   low    close
            logging.info(tse_csv)
            tse = []
            companies = []
            with open(tse_csv) as f:
                for line in f:
                    items = line.strip().split(',')
                    tse.append([
                        items[0],
                        0 if items[5] == '--' else items[5],
                        0 if items[8] == '--' else items[8],
                        0 if items[6] == '--' else items[6],
                        0 if items[7] == '--' else items[7],
                        int(int(items[2]) / 1000)
                    ])
                    companies.append([items[0], items[1]])

            # insert into table `company` (code, name, focus)
            for company in companies:
                cur.execute("SELECT code FROM company WHERE BINARY code='{}' "
                            .format(company[0]))
                res = cur.fetchall()
                if not res:
                    cur.execute("INSERT INTO company (code, name, focus) VALUES ('{}', '{}', {}) "
                                .format(company[0], company[1], 0))

            # insert to table `price` (date, company, open_price, close_price, lowest_price, highest_price)
            for company_data in tse:
                cur.execute("INSERT INTO price (date, company_code, open_price, close_price, lowest_price, highest_price, amount) "
                            "VALUES ('{}', '{}', {}, {}, {}, {}, {}) "
                            .format((s + timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S'), *company_data))

            # parse company-broker
            table = {}
            for item in tse:
                code, op, cs, lo, hi, amount = item
                if int(amount) == 0:
                    continue
                company_csv = os.path.join(args.d, d, '{}_{}.csv'.format(code, d))
                if not os.path.exists(company_csv ):
                    continue
                logging.info(company_csv)
                table[code] = {}
                with open(company_csv, 'r') as f:
                    for j, line in enumerate(f):
                        if j < 3:
                            continue
                        for row in line.split(',,'):
                            if row.strip():
                                # 序號,券商,價格,買進股數,賣出股數
                                _, broker, price, buy_amount, sell_amount = row.split(',')
                                broker = broker[:4]
                                buy_amount, sell_amount = int(int(buy_amount) / 1000), int(int(sell_amount) / 1000)
                                if broker not in table[code]:
                                    table[code][broker] = {}
                                if float(price) not in table[code][broker]:
                                    # [buy_amount, sell_amount]
                                    table[code][broker][float(price)] = [0, 0]
                                table[code][broker][float(price)][0] += buy_amount
                                table[code][broker][float(price)][1] += sell_amount

            # insert to table `tran` (date, company_code, broker_code, buy_price, buy_amount, sell_price, sell_amount)
            # one company <-> one broker
            for code in table.keys():
                for broker in table[code].keys():
                    buy_value, total_buy_amount = 0, 0
                    sell_value, total_sell_amount = 0, 0
                    for price in table[code][broker].keys():
                        buy_value += price * table[code][broker][price][0]
                        total_buy_amount += table[code][broker][price][0]
                        sell_value += price * table[code][broker][price][1]
                        total_sell_amount += table[code][broker][price][1]
                    cur.execute("INSERT INTO tran (date, company_code, broker_code, buy_price, buy_amount, sell_price, sell_amount) "
                                "VALUES ('{}', '{}', '{}', {}, {}, {}, {}) "
                                .format((s + timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S'), code, broker,
                                        0 if total_buy_amount == 0 else round(buy_value / total_buy_amount, 2), total_buy_amount,
                                        0 if total_sell_amount == 0 else round(sell_value / total_sell_amount, 2), total_sell_amount,))

            # parse otc companies
            # 0      1    2      3      4     5     6    7        8       9
            # 代號,  名稱, 收盤,   漲跌,  開盤,  最高, 最低, 均價,    成交股數, 成交金額(元)
            # code, name, close, incre, open, high, low, average, amount,  price
            logging.info(otc_csv)
            companies = []
            otc = []
            with open(otc_csv) as f:
                for line in f:
                    items = line.strip().split(',')
                    otc.append([
                        items[0],
                        0 if items[4] == '---' else items[4],
                        0 if items[2] == '---' else items[2],
                        0 if items[6] == '---' else items[6],
                        0 if items[5] == '---' else items[5],
                        int(int(items[8]) / 1000)
                    ])
                    companies.append([items[0], items[1]])

            # insert into table `company` (code, name, focus)
            for company in companies:
                cur.execute("SELECT code FROM company WHERE BINARY code='{}' "
                            .format(company[0]))
                res = cur.fetchall()
                if not res:
                    cur.execute("INSERT INTO company (code, name, focus) VALUES ('{}', '{}', {}) "
                                .format(company[0], company[1], 0))

            # insert to table `price` (date, company, open_price, close_price, lowest_price, highest_price)
            for company_data in otc:
                cur.execute("INSERT INTO price (date, company_code, open_price, close_price, lowest_price, highest_price, amount) "
                            "VALUES ('{}', '{}', {}, {}, {}, {}, {}) "
                            .format((s + timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S'), *company_data))

            # parse company-broker
            table = {}
            for item in otc:
                code, op, cs, lo, hi, amount = item
                if int(amount) == 0:
                    continue
                company_csv = os.path.join(args.d, d, '{}_{}.csv'.format(code, d))
                if not os.path.exists(company_csv):
                    continue
                logging.info(company_csv)
                table[code] = {}
                with open(company_csv, 'r') as f:
                    for j, line in enumerate(f):
                        if j < 3:
                            continue
                        for row in line.split(',,'):
                            row = row.strip()
                            if row:
                                # 序號,券商,價格,買進股數,賣出股數
                                quote_cnt = 0
                                tmp = []
                                tmp_s = ''
                                for k in range(len(row)):
                                    if row[k] == '"':
                                        quote_cnt += 1
                                    elif row[k] == ',':
                                        if quote_cnt % 2 == 0:
                                            tmp.append(tmp_s.strip())
                                            tmp_s = ''
                                    else:
                                        tmp_s += row[k]
                                tmp.append(tmp_s.strip())
                                _, broker, price, buy_amount, sell_amount = tmp
                                broker = broker[:4]
                                buy_amount, sell_amount = int(buy_amount) / 1000, int(sell_amount) / 1000
                                if broker not in table[code]:
                                    table[code][broker] = {}
                                if float(price) not in table[code][broker]:
                                    table[code][broker][float(price)] = [0, 0]
                                table[code][broker][float(price)][0] += buy_amount
                                table[code][broker][float(price)][1] += sell_amount

            # insert to table `tran` (date, company_code, broker_code, buy_price, buy_amount, sell_price, sell_amount)
            # one company <-> one broker
            for code in table.keys():
                for broker in table[code].keys():
                    buy_value, total_buy_amount = 0, 0
                    sell_value, total_sell_amount = 0, 0
                    for price in table[code][broker].keys():
                        buy_value += price * table[code][broker][price][0]
                        total_buy_amount += table[code][broker][price][0]
                        sell_value += price * table[code][broker][price][1]
                        total_sell_amount += table[code][broker][price][1]
                    cur.execute("INSERT INTO tran (date, company_code, broker_code, buy_price, buy_amount, sell_price, sell_amount) "
                                "VALUES ('{}', '{}', '{}', {}, {}, {}, {}) "
                                .format((s + timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S'), code, broker,
                                        0 if total_buy_amount == 0 else round(buy_value / total_buy_amount, 2), total_buy_amount,
                                        0 if total_sell_amount == 0 else round(sell_value / total_sell_amount, 2), total_sell_amount,))


def main():
    # args
    parser = argparse.ArgumentParser()
    day = datetime.now().strftime('%Y_%m_%d')
    parser.add_argument('-d', action='store', help='stock data directory', type=str)
    parser.add_argument('-s', action='store', help='Starting date, ex: 2017_03_09', type=str, default=day)
    parser.add_argument('-e', action='store', help='End date, ex: 2017_03_12', type=str, default=day)
    args = parser.parse_args()

    # parse
    parse(args)


if __name__ == '__main__':
    main()
