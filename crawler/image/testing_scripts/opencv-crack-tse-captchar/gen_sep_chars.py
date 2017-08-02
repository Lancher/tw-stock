#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement

# python lib
import os
import uuid
import shutil
import Queue
import sys
import uuid
import time
from datetime import datetime

# 3rd party lib
import cv2
import numpy as np
from PIL import Image
from PIL import ImageFilter


def show_img(img):
    m, n = len(img), len(img[0])
    for i in range(m):
        for j in range(n):
            if img[i][j] == 255:
                sys.stdout.write('1')
            elif img[i][j] == 254:
                sys.stdout.write('*')
            else:
                sys.stdout.write('0')
        sys.stdout.write('\n')
    sys.stdout.write('\n')


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
                if len(points) < 100:
                    for p in points:
                        img[p[0]][p[1]] = 0

    # covert all points to positive
    for i in range(m):
        for j in range(n):
            if img[i][j] == 254:
                img[i][j] = 255
            else:
                img[i][j] = 0


def split_resize_save_chars(img):
    m, n = len(img), len(img[0])        
    for i in range(len(img)):
        for j in range(len(img[i])):
            if img[i][j] == 255:
                rows = []
                cols = []
                q = Queue.Queue()

                # add first points
                img[i][j] = 254
                rows.append(i)
                cols.append(j)
                q.put((i, j))

                # bfs
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
                                rows.append(p[0]+x)
                                cols.append(p[1]+y)
                rows.sort()
                cols.sort()
                
                # grep chars 
                char_img = img[rows[0]:rows[-1], cols[0]:cols[-1]]
                char_img = cv2.resize(char_img, (40, 40))
                for a in range(len(char_img)):
                    for b in range(len(char_img[a])):
                        if char_img[a][b] == 254:
                            char_img[a][b] = 255 
                char_img_file = os.path.join(dst_folder, str(uuid.uuid4()) + '.png')
                cv2.imwrite(char_img_file, char_img)
            

def prepare_image(img):
    """Transform image to greyscale and blur it"""
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    if 'L' != img.mode:
        img = img.convert('L')
    return img


def remove_noise(img, pass_factor):
    for column in range(img.size[0]):
        for line in range(img.size[1]):
            value = remove_noise_by_pixel(img, column, line, pass_factor)
            img.putpixel((column, line), value)
    return img


def remove_noise_by_pixel(img, column, line, pass_factor):
    if img.getpixel((column, line)) < pass_factor:
        return (0)
    return (255)


src_folder = './images'
dst_folder = './images_done'

# create new folders
if os.path.isdir(dst_folder):
     shutil.rmtree(dst_folder)
os.makedirs(dst_folder)

# load images
for img_name in os.listdir(src_folder):
    img_file = os.path.join(src_folder, img_name)

    pass_factor = 210

    # remove lines noise
    img = Image.open(img_file)
    img = prepare_image(img)
    img = remove_noise(img, pass_factor)

    # pil to numpy
    img = np.asarray(img)
    img.setflags(write=1)

    # bfs
    bfs(img)

    # save sep chars
    split_resize_save_chars(img)

