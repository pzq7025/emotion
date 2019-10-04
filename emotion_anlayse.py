import pandas as pd
import re
import csv
from sklearn.pipeline import make_pipeline
import jieba
from sklearn import metrics
from sklearn.model_selection import cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split as tts


def change_data():
    # 转变获取的数据集
    with open(r'./source/file_data/spider.csv', encoding='utf-8-sig') as f:
        file_content = pd.read_csv(f)
    ids = file_content[:]['id']
    names = file_content[:]['name']
    comments = file_content[:]['comments']

    with open('./source/file_data/detail_data.csv', 'w', encoding='utf-8-sig', newline="") as f_csv:
        # 获取csv的流
        writer_buffer = csv.writer(f_csv)
        writer_buffer.writerow(["id", "comments", "star"])

        # 转换数据进行存储
        for i in range(len(ids)):
            one_result = [ids[i], names[i], comments[i]]
            if one_result[2] != "comments":
                result = detail_csv(one_result)
                writer_buffer.writerows(result)


def detail_csv(one):
    # 处理数据集转变成需要的csv格式
    """第一部分是id  名字  评论构成的三元组"""
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


def cut_word(word):
    # 对句子进行切词
    return ' '.join(jieba.lcut(word))


def get_stop_word():
    # 获取停用词
    with open('./source/detail_file/stop_word.txt', encoding='utf-8') as f:
        stop_list = [line.strip('\n') for line in f.readlines()]
    return stop_list


def read_csv():
    # 读取csv文件 并进行洗涤
    pf = pd.read_csv('./source/file_data/detail_data.csv', encoding='utf-8-sig')[['comments', 'star']]  # 获取数据
    pf['sentiment'] = pf['star'].apply(lambda i: 1 if i >= 30 else 0)  # 标签
    pf = pf.drop_duplicates()  # 去掉重复的评论
    pf = pf.dropna()  # 去除空数据

    x = pd.concat([pf[['comments']]])
    # x.columns = ['comments']
    y = pd.concat([pf.sentiment])  # 标签

    # 对句子进行分词 关键词cut_word
    x['cut_word'] = x.comments.apply(cut_word)

    x_train, x_test, y_train, y_test = tts(x, y, random_state=42, test_size=0.2)  # 按八二的数据划分结果

    stop_word = get_stop_word()

    max_df = 0.8  # 在超过这一比例的文档中出现的关键词（过于平凡），去除掉。
    min_df = 3  # 在低于这一数量的文档中出现的关键词（过于独特），去除掉。
    vector = CountVectorizer(max_df=max_df,
                             min_df=min_df,
                             token_pattern=u'(?u)\\b[^\\d\\W]\\w+\\b',
                             stop_words=frozenset(stop_word))  # 实例化 词袋模型

    nb = MultinomialNB()  # 贝叶斯

    pd.DataFrame(vector.fit_transform(x_train.cut_word).toarray(), columns=vector.get_feature_names())

    # print(pipe.steps)  # 查看pipeline的步骤（与pipeline相似）
    pipe = make_pipeline(vector, nb)
    right = cross_val_score(pipe, x_train.cut_word, y_train, cv=5, scoring='accuracy').mean()
    print(f"准确率:{right}")

    # 拟合出模型
    pipe.fit(x_train.cut_word, y_train)

    # 测试数据
    pipe.predict(x_test.cut_word)

    # 保存预测结果
    y_pred = pipe.predict(x_test.cut_word)

    # 准确率
    final_result = metrics.accuracy_score(y_test, y_pred)

    print(f"测试集的准确率:{final_result}")


if __name__ == '__main__':
    change_data()  # 洗涤数据以及处理获取数据
    read_csv()
