#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement

# 3rd party
import tornado.ioloop
import tornado.web
import tornado.options
import MySQLdb


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class API1Handler(tornado.web.RequestHandler):

    def get(self):
        # get latest date
        con = MySQLdb.connect(host='db', user='root', passwd='1234', db='stock')
        with con:
            cur = con.cursor()
            cur.execute("SELECT latest_date FROM info ORDER BY id DESC LIMIT 1")
            d = cur.fetchone()

        self.write(d)


def main():
    # tornado log
    tornado.options.parse_command_line()

    # web
    app = tornado.web.Application([
        (r"/api", MainHandler),
        (r"/api1", API1Handler),
        (r'/(.*)', tornado.web.StaticFileHandler, {'path': './frontend', "default_filename": "index.html"})
    ])
    app.listen(80)

    # run loop
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
