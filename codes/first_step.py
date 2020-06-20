from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
import os
import json
import math
import random
import numpy as np
import csv
from multiprocessing.pool import Pool


def convert(value):
    """
    convert 2------>16
    :param value: input int type
    :return: str type(16)
    """
    if value == 10:
        return "a"
    elif value == 11:
        return "b"
    elif value == 12:
        return "c"
    elif value == 13:
        return "d"
    elif value == 14:
        return "e"
    elif value == 15:
        return "f"
    return str(value)


def rgb2hex(rgb):
    """
    Convert RGB to HEX color
    :param rgb: Rge value example(23,32,44)
    :return: Hex value example #??????
    """
    hex = []
    for i in rgb:
        if i == 0:
            h = str(0) + str(0)
        else:
            h_left = int(i / 16)
            h_right = i % 16
            h = convert(h_left) + convert(h_right)

        hex.append(h)
    hex_combine = "#" + ''.join(hex)
    return hex_combine


project_name = "nature"
ID2Title = {}

with open(project_name + "/json/nature_3.json", "r") as file:
    graph = json.load(file)

with open(project_name + "/json/D.json", "r") as file:
    D = json.loads(json.load(file))

with open(project_name + "/Nature_out1_id_title.csv", "r", encoding='UTF-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    for line in tqdm(csvfile):
        row = line.split(",")
        ID2Title[int(row[0], 16)] = row[1]
nodesList = graph["nodes"]
edgesList = graph["edges"]
circles = {}
edges = []
# 将每个节点的信息写入字典circles中，以节点id做索引
Max_size = 0  # 记录节点的最大尺寸，用来调节不同层及写入文字的节点数
for node in nodesList:
    rgb = node["color"][4:-1]
    x_rgb = rgb.split(",")
    t_rgb = (int(x_rgb[0]), int(x_rgb[1]), int(x_rgb[2]))
    color = rgb2hex(t_rgb)
    circles[int(D[node["id"]], 16)] = [int(D[node["id"]], 16), node["x"], node["y"], node["size"], color]
    if node["size"] > Max_size:
        Max_size = node["size"]
# 将每个边的信息写入列表edges中
for edge in edgesList:
    S = random.random()
    if S > 0.01:
        continue
    rgb = edge["color"][4:-1]
    x_rgb = rgb.split(",")
    t_rgb = (int(x_rgb[0]), int(x_rgb[1]), int(x_rgb[2]))
    color = rgb2hex(t_rgb)
    edges.append([int(D[edge["source"]], 16), int(D[edge["target"]], 16), color])

min_x = min(float(circles[circle][1]) for circle in circles)
min_y = min(float(circles[circle][2]) for circle in circles)
max_x = max(float(circles[circle][1]) for circle in circles)
max_y = max(float(circles[circle][2]) for circle in circles)
bbox = [min_x - 100, min_y - 100, max_x + 100, max_y + 100]

real_pixel = 1024  # 先将图生成比较大的像素，然后再进行缩略图，以提高图的清晰度
request_pixel = 256  # 实际需要的切片大小


def normalize(x, y, r):
    # 去中心化，将所有圆的坐标变换到第一象限，然后除以盒子长度进行归一化，然后乘规模
    x = float(x)
    y = float(y)
    r = float(r)
    x1 = ((x - r) - bbox[0]) / (bbox[2] - bbox[0]) * scale  # 先除后乘
    y1 = ((y - r) - bbox[1]) / (bbox[3] - bbox[1]) * scale
    x2 = ((x + r) - bbox[0]) / (bbox[2] - bbox[0]) * scale
    y2 = ((y + r) - bbox[1]) / (bbox[3] - bbox[1]) * scale
    return [x1, y1, x2, y2]


def normalize_edge(x1, y1, x2, y2):
    # 同样对边进行去中心化
    x1 = float(x1)
    x2 = float(x2)
    y1 = float(y1)
    y2 = float(y2)

    x1 = (x1 - bbox[0]) / (bbox[2] - bbox[0]) * scale  # 先除后乘
    y1 = (y1 - bbox[1]) / (bbox[3] - bbox[1]) * scale
    x2 = (x2 - bbox[0]) / (bbox[2] - bbox[0]) * scale
    y2 = (y2 - bbox[1]) / (bbox[3] - bbox[1]) * scale
    return [x1, y1, x2, y2]

def judge(b, n):
    # 判断某个圆属于哪些切片，返回一个set
    # b[0]-b[3]是相当于所在切片的标号乘切片大小像素值，因此除切片大小像素值取整则得到顶点所在的排与列编号
    s = set()
    x1 = int(b[0] / real_pixel)
    y1 = int(b[1] / real_pixel)
    x2 = int(b[2] / real_pixel)
    y2 = int(b[3] / real_pixel)
    # range(x1, x2 + 1)表示该圆所接触的切片的列坐标
    # range(y1, y2 + 1)表示该圆所接触的切片的行坐标
    for i in range(x1, x2 + 1):
        for j in range(y1, y2 + 1):
            s.add(i * n + j)
    return s


for level in range(0, 10):
    print('start level', level)
    n = int(pow(2, level))
    scale = n * real_pixel  # 横向或者纵向总像素
    if not os.path.exists("%s/%d" % (project_name + "/tile", level)):
        os.mkdir("%s/%d" % (project_name + "/tile", level))
    ellipses = {i: [] for i in range(n * n)}  # for循环生成字典
    texts = {i: [] for i in range(n * n)}
    Edges = {i: [] for i in range(n * n)}
    im = Image.new("RGB", (real_pixel, real_pixel), "#000000")
    draw = ImageDraw.Draw(im)
    # 加载需要在某层绘制的节点id
    if level <= 10:
        with open(project_name + "/json/" + str(level) + ".json", "r") as file:
            level_node_list = json.loads(json.load(file))
        level_node_set = set(level_node_list)
    print("正在对节点进行划分：")
    with tqdm(circles) as t:
        try:
            for circle in t:
                if (level <= 10) and (circle not in level_node_set):
                    # 如果节点没在集合内，则不绘制
                    continue
                # 对svg中的所有节点进行遍历
                # 首先对圆的四个顶点进行处理返回归一化圆的顶点坐标
                b = normalize(circles[circle][1], circles[circle][2], circles[circle][3])
                # 对圆的归一化顶点坐标进行判定，返回一个圆被切割后所属的所有切片的一个集合，圆可能从中间切断，进而圆被分割在不同的切片中
                s = judge(b, n)
                # ellipses[i]表示第i个切片中的椭圆集合
                for i in s:
                    ellipses[i].append([b, circles[circle][4]])
                if level == 11:
                    if circles[circle][3] < 0.11:
                        #                     if circles[circle][3] < Max_size/(level + 1)**2:
                        continue
                    # 设置开始写入文字的层数
                    font_size = int((b[2] - b[0]) / 2)  # 根据节点的大小设置字体
                    font = ImageFont.truetype("arial.ttf",
                                              font_size)  # 加载一个TrueType或者OpenType字体文件，并且创建一个字体对象。这个函数从指定的文件加载了一个字体对象，并且为指定大小的字体创建了字体对象。
                    # draw.textsize(string,options)⇒ (width, height)
                    w, h = draw.textsize(ID2Title[circles[circle][0]], font)  # 返回在给定字体与字体大小的情况下字符串的尺寸，以像素为单位。
                    center = [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2]  # 计算字体中心
                    text = judge([center[0] - w / 2, center[1] - h / 2, center[0] + w / 2, center[1] + h / 2], n)
                    for i in text:
                        texts[i].append([center, font_size, ID2Title[circles[circle][0]]])
                else:
                    if circles[circle][3] < Max_size / (level + 1) ** 2:
                        continue
                    # 设置开始写入文字的层数
                    font_size = int((b[2] - b[0]) / 2)  # 根据节点的大小设置字体
                    font = ImageFont.truetype("arial.ttf",
                                              font_size)  # 加载一个TrueType或者OpenType字体文件，并且创建一个字体对象。这个函数从指定的文件加载了一个字体对象，并且为指定大小的字体创建了字体对象。
                    # draw.textsize(string,options)⇒ (width, height)
                    w, h = draw.textsize(ID2Title[circles[circle][0]], font)  # 返回在给定字体与字体大小的情况下字符串的尺寸，以像素为单位。
                    center = [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2]  # 计算字体中心
                    text = judge([center[0] - w / 2, center[1] - h / 2, center[0] + w / 2, center[1] + h / 2], n)
                    for i in text:
                        texts[i].append([center, font_size, ID2Title[circles[circle][0]]])
        except KeyboardInterrupt:
            t.close()
            raise
    t.close()
    print("正在对边进行划分：")
    try:
        with tqdm(edges) as t:
            for edge in t:
                if (level <= 10) and ((edge[0] not in level_node_set) or (edge[1] not in level_node_set)):
                    # 如果节点没在集合内，则不绘制
                    continue
                b = normalize_edge(circles[edge[0]][1], circles[edge[0]][2], circles[edge[1]][1], circles[edge[1]][2])
                # 处理由于圆弧导致的绘图区域误差
                r = math.sqrt((b[0] - b[2]) ** 2 + (b[1] - b[3]) ** 2) * 0.9
                tt = math.sqrt((b[0] - b[2]) ** 2 + (b[1] - b[3]) ** 2) * 0.5
                ttt = math.sqrt((r ** 2 - tt ** 2))
                d = r - ttt
                s = judge([min(b[0], b[2]) - d, min(b[1], b[3]) - d, max(b[0], b[2]) + d, max(b[1], b[3]) + d], n)
                for i in s:
                    try:
                        Edges[i].append([b, edge[2]])
                    except:
                        pass
    except KeyboardInterrupt:
        t.close()
        raise
    t.close()
    print("edge end!")
    eds = []
    es = []
    ts = []
    for i in tqdm(range(n * n)):
        eds.append(Edges[i])
        es.append(ellipses[i])
        ts.append(texts[i])
    numpy_eds = np.array(eds)
    np.save(project_name + '/numpy/eds%d.npy' % level, numpy_eds)
    numpy_es = np.array(es)
    np.save(project_name + '/numpy/es%d.npy' % level, numpy_es)
    numpy_ts = np.array(ts)
    np.save(project_name + '/numpy/ts%d.npy' % level, numpy_ts)

