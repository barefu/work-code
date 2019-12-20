import os

import tensorflow as tf

def picread(filelist):
    """
    读取图片并转换成张量
    :param filelist: 文件路径+名字  列表
    :return: 每张图片的张量
    """
    # 1、构造文件队列
    file_q = tf.train.string_input_producer(filelist)
    # 2、构造图片读取器（默认读取一张图片）
    reader = tf.WholeFileReader()
    label, value = reader.read(file_q)
    # 3、对读取的图片数据进行解码
    img = tf.image.decode_jpeg(value)
    label = tf.image.decode_jpeg(label)
    print(label)
    # # 4、出来图片的大小（样本统一）
    # img_resize = tf.image.resize_images(img, [94, 38])
    # print(img_resize)
    # 批处理之前样本的shape一定要固定
    img.set_shape([38, 94, 3])

    # 5、进行批处理
    img_batch, label_batch = tf.train.batch([img, label], batch_size=50, num_threads=1, capacity=1836)
    print(img_batch, label_batch)

    return img, label


if __name__ == '__main__':
    file_name = os.listdir('D:\\captcha-img\\')
    file_list = [os.path.join('D:\\captcha-img\\', file) for file in file_name]
    # example_batch, label_batch = picread(file_list)
    img, label = picread(file_list)
    with tf.compat.v1.Session() as sess:
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(sess, coord=coord)
        print(sess.run(label))
        coord.request_stop()
        coord.join(threads)
