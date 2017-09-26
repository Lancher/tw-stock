#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement

# python lib
import time
import json
import logging
import copy
import json

# 3rd party
import tornado.ioloop
import tornado.web
import tornado.options
import MySQLdb


# Use tornado default application log.
app_log = logging.getLogger('tornado.application')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class API1Handler(tornado.web.RequestHandler):

    def get(self):
        res = {'query_time': 0, 'companies': None, 'brokers': None, 'date': None}

        con = MySQLdb.connect(host='db', user='root', passwd='1234', db='stock')
        with con:
            cur = con.cursor()
            start_time = time.time()
            # get latest date
            cur.execute("SELECT latest_date FROM info ORDER BY id DESC LIMIT 1")
            d = cur.fetchone()
            res['date'] = d[0].strftime('%Y-%m-%d')

            # get company price
            cur.execute("SELECT company.code, company.name, company.focus, price.open_price, price.close_price "
                        "FROM price LEFT JOIN company ON price.company_code = company.code "
                        "WHERE price.date = '{}'".format(d[0].strftime('%Y-%m-%d')))
            res['companies'] = cur.fetchall()

            # grep brokers
            cur.execute("SELECT code, name, focus FROM broker")
            res['brokers'] = cur.fetchall()
            res['query_time'] = time.time() - start_time

        self.write(res)


class API2Handler(tornado.web.RequestHandler):

    def post(self):
        app_log.info('*'*50)
        app_log.info(self.request.body)
        app_log.info('*'*50)

        data = json.loads(self.request.body)
        res = {'query_time': 0}

        if data['type'] == 'company':
            # DB
            con = MySQLdb.connect(host='db', user='root', passwd='1234', db='stock')
            with con:
                cur = con.cursor()
                start_time = time.time()

                # get latest_date
                cur.execute("SELECT latest_date "
                            "FROM info "
                            "WHERE latest_date BETWEEN '{}' and '{}'".
                            format(data['s_date'], data['e_date']))
                rows = cur.fetchall()
                n = len(rows)
                date_index = {}
                dates = [rows[i][0].strftime('%m-%d') for i in range(n)]
                for i in range(len(rows)):
                    date_index[rows[i][0].strftime('%m-%d')] = i

                # get company
                company = {
                    'code': None,
                    'name': None,
                    'focus': None,
                    'data': [[dates[i], 0, 0, 0, 0] * 5 for i in range(n)],
                    'date': dates,
                    'amount': [None] * n
                }
                cur.execute("SELECT code, name, focus FROM company WHERE code={}".format(data['code']))
                row = cur.fetchone()
                company['code'] = row[0]
                company['name'] = row[1]
                company['focus'] = row[2]

                # get company price
                cur.execute("SELECT date, open_price, highest_price, lowest_price, close_price, amount "
                            "FROM price "
                            "WHERE company_code = {} "
                            "AND date BETWEEN '{}' AND '{}'".
                            format(company['code'], data['s_date'], data['e_date']))
                rows = cur.fetchall()
                for row in rows:
                    d = row[0].strftime('%m-%d')
                    d_i = date_index[d]
                    company['data'][d_i] = [d, str(row[1]), str(row[2]), str(row[3]), str(row[4])]
                    company['amount'][d_i] = row[5]
                res['company'] = company

                # grep brokers
                # SELECT tran.broker_code, broker.name, broker.focus, tran.date, tran.buy_amount, tran.sell_amount
                # FROM tran LEFT JOIN broker ON BINARY tran.broker_code = BINARY broker.code
                # WHERE tran.company_code = '5465' AND tran.date BETWEEN '2017-07-12' and '2017-08-11';
                cur.execute("SELECT tran.broker_code, broker.name, broker.focus, tran.date, tran.buy_amount, tran.sell_amount "
                            "FROM tran LEFT JOIN broker ON BINARY tran.broker_code = BINARY broker.code "
                            "WHERE tran.company_code = {} AND tran.date BETWEEN '{}' and '{}'".
                            format(company['code'], data['s_date'], data['e_date']))
                rows = cur.fetchall()
                brokers = {}
                for row in rows:
                    code = row[0]
                    if code not in brokers:
                        brokers[code] = {
                            'code': row[0],
                            'name': row[1],
                            'focus': row[2],
                            'date': dates,
                            'buy_amount': [0] * n,
                            'sell_amount': [0] * n,
                        }
                    d = row[3].strftime('%m-%d')
                    d_i = date_index[d]
                    brokers[code]['buy_amount'][d_i] = row[4]
                    brokers[code]['sell_amount'][d_i] = row[5]
                res['brokers'] = brokers.values()

                # query time
                res['query_time'] = time.time() - start_time

                # response
                self.write(res)

        elif data['type'] == 'broker':
            self.write(res)
        else:
            self.write(res)


def main():
    # tornado log
    tornado.options.parse_command_line()

    # web
    app = tornado.web.Application([
        (r"/api", MainHandler),
        (r"/api1", API1Handler),
        (r"/api2", API2Handler),
        (r'/(.*)', tornado.web.StaticFileHandler, {'path': './frontend', "default_filename": "index.html"})
    ])
    app.listen(80)

    # run loop
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
