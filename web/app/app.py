#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement


import tornado.ioloop
import tornado.web
import tornado.options



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def main():
    # tornado log
    tornado.options.parse_command_line()

    # web
    app = tornado.web.Application([
        (r"/api", MainHandler),
        (r'/(.*)', tornado.web.StaticFileHandler, {'path': './frontend', "default_filename": "index.html"})
    ])
    app.listen(80)

    # run loop
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
