import os

import jieba
from wordcloud import WordCloud
import pandas as pd
import matplotlib.pyplot as plt
import re
import cv2

jieba.load_userdict('./source/file_data/entity_word.txt')  # 获取停用词
font = r'C:\Windows\Fonts\simsun.ttc'  # 字体


def get_noisy_word():
    """
    获取词云的停用词
    :return:
    """
    stop_dict = {}
    with open('./source/detail_file/stop_word.txt', 'r', encoding='utf-8') as f:
        stop_word = [line.strip('\n').split(' ') for line in f.readlines()]
    for k in stop_word:
        stop_dict.update({k[0]: 0})
    return stop_dict


def create_shops():
    # 转变获取的数据集
    with open(r'./source/file_data/spider.csv', encoding='utf-8-sig') as f:
        file_content = pd.read_csv(f)
    ids = file_content[:]['id']
    names = file_content[:]['name']
    comments = file_content[:]['comments']

    # 转换数据进行存储
    shop_dict = {}
    for i in range(len(ids)):
        one_result = [ids[i], names[i], comments[i]]
        if one_result[2] != "comments":
            result = detail_csv(one_result)
            shop_dict.update({one_result[1]: len(result)})
    path = r'./source/picture_data/peace.png'  # 自定义的图片
    create_cloud_pic(shop_dict, type_c='dict', pic_name='shop_name', img_path=path)


def detail_csv(one):
    # 处理数据集转变成需要的csv格式
    """
    :param one: 第一部分是id  名字  评论构成的三元组
    :return:
    """
    content = str(one[2])
    sentence = content.split('$')
    record = []
    for i in sentence:
        part = i.split('————————')
        part[0] = re.compile(r"\W+", re.S).sub('', part[0]).replace('٩๑ơలơ۶', '')
        if len(part) >= 2:  # 去掉没有评分的数据
            if part[0]:
                record.append([one[0], part[0], part[1]])
    return record


def creat_comments():
    with open(r'./source/file_data/spider.csv', encoding='utf-8-sig') as f:
        file_content = pd.read_csv(f)
    ids = file_content[:]['id']
    names = file_content[:]['name']
    comments = file_content[:]['comments']

    # 转换数据进行存储
    final_result = []
    for i in range(len(ids)):
        one_result = [ids[i], names[i], comments[i]]
        if one_result[2] != "comments":
            result = detail_csv(one_result)
            if result:
                for t in result:
                    final_result.append(' '.join(jieba.lcut(t[1])))

    content = ' '.join(final_result)

    #
    path = r'./source/picture_data/play.jpg'  # 自定义的图片
    create_cloud_pic(content, type_c='str', pic_name='comments', img_path=path)


def create_cloud_pic(content, type_c, pic_name, img_path):
    """

    :param pic_name: 图片文件名
    :param img_path: 传入图片地址
    :param type_c: 保存的类型
    :param content: 字典形式的内容
    :return:
    """
    stopwords = get_noisy_word()  # 噪声词以字典的形式进行呈现
    img = cv2.imread(img_path)  # 图片矩阵
    cloud = WordCloud(
        # 设置字体，不指定就会出现乱码
        font_path=font,  # 这个路径是pc中的字体路径
        # 设置背景色
        background_color='white',
        # 词云形状
        mask=img,
        # 允许最大词汇
        max_words=50,
        # 最大号字体
        max_font_size=100,
        # 过滤噪声词
        stopwords=stopwords,
        # 设置有多少种随机生成状态，即有多少种配色方案
        random_state=30,
        # scale=1 # 模糊度
    )
    global word_cloud
    if type_c == 'dict':
        word_cloud = cloud.generate_from_frequencies(content)  # 产生词云,输入的格式是以空格分隔的词语组成的字符串
    if type_c == 'str':
        word_cloud = cloud.generate(content)  # 可视化字符
    path = './source/picture_create/'
    if not path:
        os.makedirs(path)
    word_cloud.to_file("./source/picture_create/" + str(pic_name) + ".jpg")  # 保存图片
    #  显示词云图片
    plt.imshow(word_cloud)
    plt.axis('off')
    plt.show()


if __name__ == '__main__':
    create_shops()  # 店铺
    creat_comments()  # 评论
