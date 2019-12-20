import os

import tensorflow as tf

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('img_dir', 'D:\captcha-img-deal', '图片文件的目录')
tf.app.flags.DEFINE_string('tfrecords_dir', './tfrecords/train_2.tfrecords', 'tfrecords存储目录')
tf.app.flags.DEFINE_string('letter', 'abcdefghijklmnopqrstuvwxyz0123456789', 'tfrecords存储目录')


def get_captcha_image():
    """
    获取验证码图片数据
    :param self: file_list：路径 + 名字列表
    :return: image
    """
    file_name = os.listdir(FLAGS.img_dir)
    # 构造路径+文件
    file_list = [os.path.join(FLAGS.img_dir, file) for file in file_name]
    # 构造文件队列
    file_q = tf.train.string_input_producer(file_list, shuffle=False)
    # 构造阅读器
    reader = tf.WholeFileReader()
    # 读取图片数据内容
    key, value = reader.read(file_q)
    # 解码图片数据
    image = tf.image.decode_jpeg(value)
    # 出来图片的大小（样本统一）
    img_resize = tf.image.resize_images(image, [38, 94])
    img_resize.set_shape([38, 94, 1])
    # x = [100, 38*94*3]  y_p = [100, 4*36]  w = [38*94*3, 4*36] b = [4*36]
    # 批处理数据
    image_batch = tf.train.batch([img_resize], batch_size=2209, num_threads=1, capacity=3000)
    return image_batch


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
    print(letter_num)
    # 构建标签的列表
    array = []
    # 给标签数据进行处理
    for string in label_str:
        letter_list = []
        for letter in string:
            try:
                letter_list.append(letter_num[letter])
            except:
                print(string)
        array.append(letter_list)
    label = tf.constant(array)
    # print(label)
    return label


def tfrecords_write(label_batch, image_batch):
    """
    将图片内容和标签写入tfrecords文件中
    :return: None
    """
    print(label_batch, image_batch)
    # 建立tfrecords存储器
    label_batch = tf.cast(label_batch, tf.uint8)
    writer = tf.python_io.TFRecordWriter(FLAGS.tfrecords_dir)
    for i in range(2209):
        image = image_batch[i].eval().tostring()
        label = label_batch[i].eval().tostring()
        print(label_batch[i].eval())
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


if __name__ == '__main__':
    file_name = os.listdir(FLAGS.img_dir)
    capthca_list = [name.split('.')[0] for name in file_name]
    # 获取label， image
    label = deal_label(capthca_list)
    image_batch = get_captcha_image()
    with tf.compat.v1.Session() as sess:
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(sess=sess, coord=coord)
        tfrecords_write(label, image_batch)
        coord.request_stop()
        coord.join(threads)
