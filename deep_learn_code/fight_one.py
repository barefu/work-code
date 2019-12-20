import os

import numpy as np
import requests
import tensorflow as tf
from PIL import Image, ImageEnhance


# 定义初始化权重的函数
def weight_variables(shape):
    w = tf.Variable(tf.random_normal(shape=shape, mean=0.0, stddev=1.0))
    return w


# 定义初始化偏置的函数
def bbias_variables(shape):
    b = tf.Variable(tf.random_normal(shape=shape, mean=0.0, stddev=1.0))
    return b


def captcha_img_download(name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
    }
    base_url = 'http://222.143.21.205:8081/captcha-image'
    res = requests.get(base_url, headers=headers)
    path = 'D:\\work-content\\tf_study\\img_text\\{}'.format(name)
    with open(path, "wb")as f:
        f.write(res.content)
        f.close()
        print("文件保存成功！")
    image_data = Image.open(path)
    image_data = image_data.convert('L')
    im = ImageEnhance.Contrast(image_data)
    im = im.enhance(4)
    im = im.convert('L')
    im.save('D:\\work-content\\tf_study\\img_text\\1234.png')
    im = np.array(im)
    return im


def img_read():
    file_name = os.listdir('D:\\captcha-img-deal')
    names = [name.split('.')[0] for name in file_name]
    l = [os.path.join('D:\\captcha-img-deal', name) for name in file_name]
    i = 900
    image_data = Image.open(l[i])
    name = names[i]
    return image_data, name


def predict(image):
    with tf.variable_scope('model'):
        # 将图片数据转换二维
        img = tf.to_float(image, name='ToFloat')
        image_reshape = tf.reshape(img, [-1, 38 * 94 * 1])
        # 1、随机初始化权重，偏置
        weights = weight_variables([38 * 94 * 1, 4 * 36])
        bias = bbias_variables([4 * 36])
        # 进行全连接层计算
        y_predict = tf.matmul(image_reshape, weights) + bias
        return y_predict


if __name__ == '__main__':
    letter = 'abcdefghijklmnopqrstuvwxyz0123456789'
    num_letter = dict(enumerate(list(letter)))

    with tf.compat.v1.Session() as sess:
        name = '{}.png'.format('12')
        image_data = captcha_img_download(name)
        # image_data, name = img_read()
        y_predict = predict(image_data)
        saver = tf.train.Saver()
        saver.restore(sess, './ckpt/captcha_model')
        num_list = tf.argmax(tf.reshape(sess.run(y_predict), [4, 36]), 1).eval()
        predict_str = num_letter[num_list[0]]+num_letter[num_list[1]]+num_letter[num_list[2]]+\
                      num_letter[num_list[3]]
        print('预测结果是：{}'.format(predict_str), name)



