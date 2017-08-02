#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement

# python lib
import json
import logging
import socket
import subprocess
import time
import pprint
import datetime
from datetime import timedelta, date
import shutil
import uuid
import os
import Queue
import sys

# 3rd party lib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from PIL import Image
from PIL import ImageFilter
import cv2
import numpy as np
import tornado.web
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPResponse
from tornado.httpclient import HTTPError
from tornado import ioloop
from tornado.options import define, options
from tornado.locks import Semaphore


# Use tornado default log.
app_log = logging.getLogger("tornado.application")


def bfs(img):
    m, n = len(img), len(img[0])
    for i in range(m):
        for j in range(n):
            if img[i][j] == 255:
                points = []
                q = Queue.Queue()

                # add first white point
                img[i][j] = 254
                q.put((i, j))
                points.append((i, j))

                # BFS
                while not q.empty():
                    sz = q.qsize()
                    for _ in range(sz):
                        p = q.get()
                        x, y = 0, 1
                        for i in range(4):
                            x, y = y, -x
                            if 0 <= p[0] + x < m and 0 <= p[1] + y < n and img[p[0]+x][p[1]+y] == 255:
                                img[p[0]+x][p[1]+y] = 254
                                q.put((p[0]+x, p[1]+y))
                                points.append((p[0]+x, p[1]+y))

                # erase small groups
                if len(points) < 50:
                    for p in points:
                        img[p[0]][p[1]] = 0

    # covert all points to positive
    for i in range(m):
        for j in range(n):
            if img[i][j] == 254:
                img[i][j] = 255
            else:
                img[i][j] = 0


def divide_by_lines(img):
    m, n = len(img), len(img[0])
    for i in range(m):
        for j in [27, 28, 29, 51, 52, 53, 77, 78, 79, 100, 101, 102]:
            img[i][j] = 0


def erase_lines(img):
    m, n = len(img), len(img[0])
    # horizetal lines
    for i in range(0, m):
        points = []
        for j in range(n):
            if img[i][j] == 255 and (i == 0 or img[i-1][j] == 0) and (i == m -1 or img[i+1][j] == 0):
                points.append((i, j))
            else:
                # 4 continous points
                if len(points) > 4:
                    for p in points:
                        img[p[0]][p[1]] = 0
                points = []

    # vertical lines
    for j in range(1, n - 1):
        points = []
        for i in range(m):
            if img[i][j] == 255 and img[i][j-1] == 0 and img[i][j+1] == 0:
                points.append((i, j))
            else:
                # 4 continous points
                if len(points) > 4:
                    for p in points:
                        img[p[0]][p[1]] = 0
                points = []


def split_resize_save_chars(img):
    divs = [0, 28, 52, 78, 101, 130]
    imgs = []
    for i in range(5):
        char_img = img[0:30, divs[i]:divs[i+1]]
        
        rows, cols = [], []
        for i in range(len(char_img)):
            for j in range(len(char_img[0])):
                if char_img[i][j] == 255:
                    rows.append(i)
                    cols.append(j)
        rows.sort()
        cols.sort()
        char_img = char_img[rows[0]:rows[-1], cols[0]:cols[-1]]
        char_img = cv2.resize(char_img, (40, 40))        

        imgs.append(char_img)
    return imgs


def load_samples():
    samples = {}
    for ch in os.listdir('samples'):
        if ch not in samples:
            samples[ch] = []
        for img_name in os.listdir(os.path.join('samples', ch)):
            img = cv2.imread(os.path.join('samples', ch, img_name))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            samples[ch].append(img)
    return samples


def mse(img1, img2):
    err = np.sum((img1.astype('float') - img2.astype('float')) ** 2)    
    err /= float(img1.shape[0] * img1.shape[1])
    return err


class MainHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.samples = load_samples()

    def get(self):
        # get file
        f = self.get_argument('f')

        img = cv2.imread(f)

        # gray
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.bitwise_not(img)

        # white black
        img = cv2.threshold(img, 135, 255, cv2.THRESH_BINARY)[1]

        # erode
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.erode(img, kernel, iterations=1)

        # erase noises
        divide_by_lines(img)
        bfs(img)
        erase_lines(img)
        bfs(img)
        # show_img(img)

        # split to chars
        imgs = split_resize_save_chars(img)

        # find minimum mse
        captchat = []
        for img in imgs:
            result = ['', None]
            for ch, cmp_imgs in self.samples.iteritems():
                for cmp_img in cmp_imgs:
                    err = mse(cmp_img, img)
                    if result[1] == None or err < result[1]:
                        result = [ch, err]
            captchat.append(result[0])

        self.write(''.join(captchat))
        app_log.info(''.join(captchat))


def main():
    # tornado log
    options.parse_command_line()

    # web
    app = tornado.web.Application([
        (r"/", MainHandler),
    ])
    app.listen(8889, address='127.0.0.1')

    # run loop
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()



