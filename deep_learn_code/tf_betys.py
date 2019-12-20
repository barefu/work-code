import tensorflow as tf
import os

# 定义cifar数据的命令行参数
FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('cifar_dir', './cifar10/', '文件的目录')
tf.app.flags.DEFINE_string('cifar_tfrecords', './tfrecords/cifar.tfrecords', 'tfrecords存储目录')

class CifarRead(object):
    """
    读取二进制文件转化张量,写进tfrecords,读取tfrecords
    """
    def __init__(self, filelist):
        # 文件列表
        self.filelist = filelist
    #     定义图片的一些属性
        self.height = 32
        self.width = 32
        self.channel = 3
        # 存储字节数
        self.label_bytes = 1
        self.img_bytes = self.height * self.width * self.channel
        self.bytes = self.label_bytes + self.img_bytes


    def read_decode(self):
        # 1、构造文件队列
        file_q = tf.train.string_input_producer(self.filelist)
        # 2、构造二进制文件读取器、读取数据,定义每个样本的字节数
        reader = tf.FixedLengthRecordReader(self.bytes)
        key, value = reader.read(file_q)
        print(value)
        # 3.解码数据,二进制
        label_img = tf.decode_raw(value, tf.uint8)
        # 4、分割出图片和标签
        label = tf.cast(tf.slice(label_img, [0], [self.label_bytes]), tf.int32)
        img = tf.slice(label_img, [self.label_bytes], [self.img_bytes])
        # 5、对图片的特征数据进行改变 [3072]  -->[32, 32, 3]
        img_reshape = tf.reshape(img, [self.height, self.width, self.channel])
        print(label, img_reshape)
        # 6、批处理
        label_batch, img_batch = tf.train.batch([label, img_reshape], batch_size=20, num_threads=10, capacity=20)
        print(label_batch, img_batch)

        return label_batch, img_batch

    def writer_tfrecords(self, img_batch, label_batch):
        """
        将图片的特征值和目标值存进tfrecords
        :param img_brach: 10张图片的特征值
        :param label_batch: 10张图片的目标值
        :return:None
        """
        # 1、构造tfrecords存储器
        writer = tf.python_io.TFRecordWriter(FLAGS.cifar_tfrecords)
        # 2、循环将所有样本写入，每个样本都要构造example协议
        for i in range(10):
            img = img_batch[i].eval().tostring()
            label = label_batch[i].eval()[0]
            # 构造样本的example协议
            example = tf.train.Example(features=tf.train.Features(feature={
                'image': tf.train.Feature(bytes_list=tf.train.BytesList(value=[img])),
                'label': tf.train.Feature(int64_list=tf.train.Int64List(value=[label])),
            }))

            # 写入单独的样本
            writer.write(example.SerializeToString())

        # 关闭存储器
        writer.close()
        return None

    def read_tfrecords(self):
        # 1、构造文件队列
        file_q = tf.train.string_input_producer([FLAGS.cifar_tfrecords])
        # 2、构建文件阅读器，读取内容example, value=一个样本的序列化example
        reader = tf.TFRecordReader()
        key, value = reader.read(file_q)
        # 3、解析example
        features = tf.parse_single_example(value, features={
            'image': tf.FixedLenFeature([], tf.string),
            'label': tf.FixedLenFeature([], tf.int64)
        })

        # 4、解码内容,如果读取的格式为string需要解码，而int，float不需要解码
        image = tf.decode_raw(features['image'], tf.int8)
        # 固定图片的shape，方便批处理
        img_reshape = tf.reshape(image, [self.height, self.width, self.channel])

        label = tf.cast(features['label'], tf.int32)
        print(img_reshape, label)

        # 进行批处理
        img_batch, label_batch = tf.train.batch([img_reshape, label], batch_size=10, num_threads=1, capacity=10)

        return img_batch, label_batch


if __name__ == '__main__':
    file_name = os.listdir(FLAGS.cifar_dir)
    file_list = [os.path.join(FLAGS.cifar_dir, file) for file in file_name if file[-3:] == 'bin']
    cf = CifarRead(file_list)
    img_batch, label_batch = cf.read_tfrecords()
    with tf.compat.v1.Session() as sess:
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(sess, coord=coord)
        # 存进tfrecords文件
        # print('开始存储')
        # cf.writer_tfrecords(img_batch, label_batch)
        # print('结束存储')

        print(sess.run([label_batch, img_batch]))

        coord.request_stop()
        coord.join()