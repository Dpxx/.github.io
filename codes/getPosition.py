import json
import time
from tqdm import tqdm
import csv

with open("nature/json/nature_3.json", "r") as file:
    graph = json.load(file)
# D : id -> id16
with open("nature/json/D.json", "r") as file:
    D = json.loads(json.load(file))
nodesList = graph["nodes"]
min_x = 10000
min_y = 10000
max_x = -10000
max_y = -10000
for i in nodesList:
    min_x = min(min_x, i["x"])
    min_y = min(min_y, i["y"])
    max_x = max(max_x, i["x"])
    max_y = max(max_y, i["y"])

bbox = [min_x - 100, min_y - 100, max_x + 100, max_y + 100]

def normalize(x, y, r):
    # 去中心化，将所有圆的坐标变换到第一象限，然后除以盒子长度进行归一化，然后乘规模
    x = float(x)
    y = float(y)
    r = float(r)
    x1 = ((x - r) - bbox[0]) / (bbox[2] - bbox[0])  # 先除后乘
    y1 = ((y - r) - bbox[1]) / (bbox[3] - bbox[1])
    x2 = ((x + r) - bbox[0]) / (bbox[2] - bbox[0])
    y2 = ((y + r) - bbox[1]) / (bbox[3] - bbox[1])
    return [x1, y1, x2, y2]

dic = {}  # id16 -> position dictionary
for i in tqdm(nodesList):
    x0 = i["x"]
    y0 = i["y"]
    b = normalize(x0,y0,i["size"])
    center = [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2]
    center = [round(i, 5) for i in center]
    dic[D[i["id"]]] = center


csv.field_size_limit(500 * 1024 * 1024)
csv_data = csv.reader(open("nature/Nature_out1_id_title.csv",encoding='utf-8'))
titles = {}  # id16 -> title
for i in csv_data:
    titles[i[0]] = i[1]

# for i in tqdm(nodesList):
#     if D[i["id"]] == "753FC43B" or D[i["id"]] == "62DF29B8":
#         print(i)

final = {}
for level in range(0, 2):
    print('start level', level)
    # 加载需要在某层绘制的节点id
    with open("nature/json/" + str(level) + ".json", "r") as file:
        level_node_list = json.loads(json.load(file))
    level_node_set = set(level_node_list)
    for i in tqdm(level_node_list):  # id
        try:
            final[titles[str(hex(i)[2:]).upper()]] = dic[str(hex(i)[2:]).upper()]
        except:
            continue

filename = 'nature/json/title_position.json'
with open(filename,'w') as file_obj:
    json.dump(final, file_obj)
