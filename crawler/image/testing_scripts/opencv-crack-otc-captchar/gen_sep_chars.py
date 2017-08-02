import os
import uuid
import shutil
import cv2
import numpy as np
import Queue
import sys

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

        char_img_file = os.path.join(dst_folder, str(uuid.uuid4()) + '.png')
        cv2.imwrite(char_img_file, char_img)    

    


src_folder = './images'
dst_folder = './images_done'

# create new folders
if os.path.isdir(dst_folder):
     shutil.rmtree(dst_folder)
os.makedirs(dst_folder)

# load images
for img_name in os.listdir(src_folder):
    img_file = os.path.join(src_folder, img_name)
    
    img = cv2.imread(img_file)

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

    # split to chars
    split_resize_save_chars(img)





