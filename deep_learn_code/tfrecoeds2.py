import numpy as np
import tensorflow as tf
from PIL import Image, ImageEnhance
import os

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('img_dir', 'D:\captcha-img', '图片文件的目录')
tf.app.flags.DEFINE_string('tfrecords_dir', './tfrecords/train_3.tfrecords', 'tfrecords存储目录')
tf.app.flags.DEFINE_string('letter', 'abcdefghijklmnopqrstuvwxyz0123456789', 'tfrecords存储目录')


def deal_label(label_str):
    """
    处理验证码
    :param self: None
    :return: label
    """
    # 构建字符索引 {0：'a', 1：'b', ........}
    num_letter = dict(enumerate(list(FLAGS.letter)))
    # 键值翻转{a：'0', b：'1', ........}
    letter_num = dict(zip(num_letter.values(), num_letter.keys()))
    # 构建标签的列表
    array = []
    # 给标签数据进行处理
    for string in label_str:
        letter_list = []
        for letter in string:
            try:
                letter_list.append(letter_num[letter])
            except:
                pass
                print(letter)
        array.append(letter_list)
    # label = tf.constant(array)
    return array


def tfrecords_write(labels):
    """
    将图片内容和标签写入tfrecords文件中
    :return: None
    """
    # 建立tfrecords存储器
    writer = tf.python_io.TFRecordWriter(FLAGS.tfrecords_dir)
    file_name = os.listdir(FLAGS.img_dir)
    capthca_dir = [os.path.join('D:\\captcha-img', name) for name in file_name]
    for i in range(len(labels)):
        label = labels[i]
        label = tf.cast(label, tf.uint8)
        image = get_captcha_image(capthca_dir[i])
        image = tf.constant(image)
        image = image.eval().tostring()
        label = label.eval().tostring()
        # 构造example
        example = tf.train.Example(features=tf.train.Features(feature={
            'image': tf.train.Feature(bytes_list=tf.train.BytesList(value=[image])),
            'label': tf.train.Feature(bytes_list=tf.train.BytesList(value=[label]))
        }))
        writer.write(example.SerializeToString())
        print('第{}张写入成功！'.format(i))
    # 关闭文件
    writer.close()
    return None


def get_captcha_image(dir):
    image_data = Image.open(dir)
    im = ImageEnhance.Contrast(image_data)
    im = im.enhance(4)
    image_data = np.array(image_data.convert('L'))
    return image_data


if __name__ == '__main__':
    file_name = os.listdir(FLAGS.img_dir)
    capthca_names = [name.split('.')[0] for name in file_name]
    capthca_dir = [os.path.join('D:\\captcha-img', name) for name in file_name]
    label_list = deal_label(capthca_names)
    with tf.compat.v1.Session() as sess:
        tfrecords_write(label_list)
        # for i in range(len(label_list)):
        #     image = get_captcha_image(capthca_dir[i])
        #     label = label_list[i]
        #     tfrecords_write(label, image)
        #     print('第{}张写入成功！'.format(i))
