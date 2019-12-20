import tensorflow as tf
import os


def file_read(filelist):
    """
    读取csv文件
    :param filelist: 文件路径+名字 的列表
    :return: 每个样本行内容
    """
    # 1、构造文件队列
    file_q = tf.train.string_input_producer(filelist)
    # 2、构造阅读器，读取队列数据
    reader = tf.TextLineReader()
    key, value = reader.read(file_q)
    # 3、对每个样本行数据解码
    # record_defaults:指定每个样本行每一列的类型，指定默认值
    record = [['None'], ['None']]
    example, label = tf.decode_csv(value, record_defaults=record)
    # 4、批处理，每次读取多个数据，批处理大小，跟队列，数据的数量没有关系，只决定这批次处理多少数据
    example_batch, label_batch = tf.train.batch([example, label], batch_size=9, num_threads=1, capacity=9)
    print(example_batch, label_batch)
    return example_batch, label_batch


if __name__ == '__main__':
    # 找到文件，放入列表  路径+名字
    file_name = os.listdir('./file/')
    filelist = [os.path.join('./file/', file) for file in file_name]
    example_batch, label_batch = file_read(filelist)

    with tf.compat.v1.Session() as sess:
        # 定义线程管理器
        coord = tf.train.Coordinator()
        # 开启读取文件的线程
        threads = tf.train.start_queue_runners(sess, coord=coord)

        # 打印读取的内容
        print(sess.run([example_batch, label_batch]))

        # 回收线程

        coord.request_stop()
        coord.join(threads)
