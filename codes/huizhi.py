from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
import os
import json
import math
import random
import csv
import numpy as np
from multiprocessing.pool import Pool

real_pixel = 1024


def draw_edge(draw, x1, y1, x2, y2, fill):
    r = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) * 0.9
    try:
        c1 = (x2 ** 2 - x1 ** 2 + y2 ** 2 - y1 ** 2) / (2 * (x2 - x1))
        c2 = (y2 - y1) / (x2 - x1)
    except:
        x1 = x1 + 0.01
        c1 = (x2 ** 2 - x1 ** 2 + y2 ** 2 - y1 ** 2) / (2 * (x2 - x1))
        c2 = (y2 - y1) / (x2 - x1)
    A = (c2 ** 2 + 1)
    B = (2 * x1 * c2 - 2 * c1 * c2 - 2 * y1)
    C = (x1 ** 2 - 2 * x1 * c1 + c1 ** 2 + y1 ** 2 - r ** 2)
    try:
        y = (-B + math.sqrt(B * B - 4 * A * C)) / (2 * A)
    except:
        y = (-B) / (2 * A)
    x = c1 - c2 * y
    th_1 = math.atan((y - y1) / (x1 - x))
    if x1 < x:
        th_1 = th_1 + 3.1415926
    th_2 = math.atan((y - y2) / (x2 - x))
    if x2 < x:
        th_2 = th_2 + 3.1415926
    if th_1 < 0:
        th_1 = 6.2831852 + th_1
    if th_2 < 0:
        th_2 = 6.2831852 + th_2
    th_1 = 360 - th_1 / 3.1415926 * 180
    th_2 = 360 - th_2 / 3.1415926 * 180
    if th_2 - th_1 >= 0:
        D_th = th_2 - th_1
    else:
        D_th = th_2 - th_1 + 360
    if D_th >= 180:
        try:
            y = (-B - math.sqrt(B * B - 4 * A * C)) / (2 * A)
        except:
            y = (-B) / (2 * A)
        x = c1 - c2 * y
        th_1 = math.atan((y - y1) / (x1 - x))
        if x1 < x:
            th_1 = th_1 + 3.1415926
        th_2 = math.atan((y - y2) / (x2 - x))
        if x2 < x:
            th_2 = th_2 + 3.1415926
        th_1 = 360 - th_1 / 3.1415926 * 180
        th_2 = 360 - th_2 / 3.1415926 * 180
        draw.arc((x - r, y - r, x + r, y + r), th_1, th_2, fill=fill)
    else:
        draw.arc((x - r, y - r, x + r, y + r), th_1, th_2, fill=fill)


def worker(args):
    idx, eds, es, ts = args
    i = idx // n
    j = idx % n
    if os.path.exists(r"D:\jiaoda\Project_new\img\%d\%d\%d.png" % (level, i, j)):
        print("exist")
        return
    im = Image.new("RGB", (real_pixel, real_pixel), "#000000")
    draw = ImageDraw.Draw(im)
    # ellipses和texts中均包含所有与该切片接触的圆和文字
    for ed in eds:
        draw_edge(draw, ed[0][0] - real_pixel * i, ed[0][1] - real_pixel * j, ed[0][2] - real_pixel * i,
                  ed[0][3] - real_pixel * j, fill=ed[1])
    for e in es:
        draw.ellipse([e[0][0] - real_pixel * i, e[0][1] - real_pixel * j, e[0][2] - real_pixel * i,
                      e[0][3] - real_pixel * j], fill=e[1])  # 存在去中心化的过程，将第一象限的切片变换到坐标原点
    for t in ts:
        font = ImageFont.truetype("arial.ttf", t[1])
        w, h = draw.textsize(t[2], font)
        draw.text([t[0][0] - w / 2 - real_pixel * i, t[0][1] - h / 2 - real_pixel * j], t[2], fill="#ffffff",
                  font=font)
    del draw
    # 生成缩略图
    # im.thumbnail((256, 256))
    im.save(r"D:\jiaoda\Project_new\img\%d\%d\%d.png" % (level, i, j), "PNG")


if __name__ == '__main__':
    for i in range(0, 11):
        level = i
        n = int(pow(2, level))

        # for ii in tqdm(range(n)):
        #     if not os.path.exists("nature/tile/%d/%d" % (level, ii)):
        #         os.mkdir("nature/tile/%d/%d" % (level, ii))

        eds = np.load('nature/numpy/eds%d.npy' % i, allow_pickle=True)
        es = np.load('nature/numpy/es%d.npy' % i, allow_pickle=True)
        ts = np.load('nature/numpy/ts%d.npy' % i, allow_pickle=True)
        print("正在绘制切片%d：" % i)
        with Pool(30) as pool:
            pool.map(worker, zip(range(n * n), eds, es, ts))

        print("level %d finish" % i)
