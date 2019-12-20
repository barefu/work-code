import math
import os

import tensorflow as tf

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('img_dir', 'D:\captcha-img-deal', '图片文件的目录')
tf.app.flags.DEFINE_string('letter', 'abcdefghijklmnopqrstuvwxyz0123456789', 'tfrecords存储目录')


# 定义初始化权重的函数
def weight_variable(shape):
    w = tf.Variable(tf.random_normal(shape=shape, mean=0.0, stddev=1.0))
    return w


# 定义初始化偏置的函数
def bias_variable(shape):
    b = tf.Variable(tf.random_normal(shape=shape, mean=0.0, stddev=1.0))
    return b


def label_to_onehot(label):
    """
    将读取文件中的目标值转换onehot编码
    :param label:
    :return: one_hot
    """
    one_hot = tf.one_hot(label, depth=36, on_value=1.0, axis=2)
    return one_hot


def fc_model(image):
    """
    进行预测结果
    :param image:50张图片数据
    :return: 预测值
    """
    with tf.variable_scope('model'):
        # 将图片数据转换二维
        image_reshape = tf.reshape(image, [-1, 38 * 94 * 1])
        # 1、随机初始化权重，偏置
        weights = weight_variable([38 * 94 * 1, 4 * 36])
        bias = bias_variable([4 * 36])
        # 进行全连接层计算
        y_predict = tf.matmul(image_reshape, weights) + bias

    return y_predict


def create_model(self, x_images, keep_prob):
    # first layer
    w_conv1 = self.weight_variable([5, 5, 1, 32])
    b_conv1 = self.bias_variable([32])
    h_conv1 = tf.nn.relu(tf.nn.bias_add(self.conv2d(x_images, w_conv1), b_conv1))
    h_pool1 = self.max_pool_2x2(h_conv1)
    h_dropout1 = tf.nn.dropout(h_pool1, keep_prob)
    conv_width = math.ceil(self.width / 2)
    conv_height = math.ceil(self.height / 2)

    # second layer
    w_conv2 = self.weight_variable([5, 5, 32, 64])
    b_conv2 = self.bias_variable([64])
    h_conv2 = tf.nn.relu(tf.nn.bias_add(self.conv2d(h_dropout1, w_conv2), b_conv2))
    h_pool2 = self.max_pool_2x2(h_conv2)
    h_dropout2 = tf.nn.dropout(h_pool2, keep_prob)
    conv_width = math.ceil(conv_width / 2)
    conv_height = math.ceil(conv_height / 2)

    # third layer
    w_conv3 = self.weight_variable([5, 5, 64, 64])
    b_conv3 = self.bias_variable([64])
    h_conv3 = tf.nn.relu(tf.nn.bias_add(self.conv2d(h_dropout2, w_conv3), b_conv3))
    h_pool3 = self.max_pool_2x2(h_conv3)
    h_dropout3 = tf.nn.dropout(h_pool3, keep_prob)
    conv_width = math.ceil(conv_width / 2)
    conv_height = math.ceil(conv_height / 2)

    # first fully layer
    conv_width = int(conv_width)
    conv_height = int(conv_height)
    w_fc1 = self.weight_variable([64 * conv_width * conv_height, 1024])
    b_fc1 = self.bias_variable([1024])
    h_dropout3_flat = tf.reshape(h_dropout3, [-1, 64 * conv_width * conv_height])
    h_fc1 = tf.nn.relu(tf.nn.bias_add(tf.matmul(h_dropout3_flat, w_fc1), b_fc1))
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    # second fully layer
    w_fc2 = self.weight_variable([1024, self.char_num * self.classes])
    b_fc2 = self.bias_variable([self.char_num * self.classes])
    y_conv = tf.add(tf.matmul(h_fc1_drop, w_fc2), b_fc2)

    return y_conv


def read_data():
    """
    从文件读取数据  图片 + 标签
    :return: batch  of image and label
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
    # x = [-1, 38*94*3]  y_p = [-1, 4*36]  w = [38*94*3, 4*36] b = [4*36]
    # 批处理数据
    image_batch = tf.train.batch([img_resize], batch_size=2209, num_threads=1, capacity=3000)
    return image_batch


def deal_label():
    """
    处理验证码
    :param self: label_str
    :return: label
    """
    file_name = os.listdir(FLAGS.img_dir)
    capthca_list = [name.split('.')[0] for name in file_name]
    label_str = capthca_list
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
    return label


def captcharec():
    # 1、获取验证码的数据文件
    img_batch = read_data()
    label_batch = deal_label()
    # 2、通过输入图片特征数据，建立模型，得出预测结果
    # 一层，全连接神经网络
    y_predict = fc_model(img_batch)  # [-1, 144]
    # 3、目标值转换为one_hot  [-1, 4, 36]
    y_ture = label_to_onehot(label_batch)

    # 4、softmax计算， 交叉熵损失计算
    with tf.variable_scope('soft_cross'):
        # 求平均交叉熵损失值, y_ture [100, 4, 36] ---> [100, 144]
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(
            labels=tf.reshape(y_ture, [50, 144]),
            logits=y_predict
        ))

        # 5、梯度下降求出损失
    with tf.variable_scope('optimizer'):
        train_op = tf.train.GradientDescentOptimizer(0.01).minimize(loss)

        # 6、计算准确率   argmax(值列表， [axis])
    with tf.variable_scope('acc'):
        # 比较每个预测值和目标值是否（4个）位置一样
        equal_list = tf.equal(tf.argmax(y_ture, 2), tf.argmax(tf.reshape(y_predict, [50, 4, 36]), 2))
        accuracy = tf.reduce_mean(tf.cast(equal_list, tf.float32))

    # 创建一个saver
    saver = tf.train.Saver()

    # init_op = tf.global_variables_initializer()
    init_op = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
    with tf.compat.v1.Session() as sess:
        sess.run(init_op)
        # 开启线程协调器， （有数据在文件当中读取提供给模型）
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(sess=sess, coord=coord)
        # print(label_batch[1].eval(), img_batch[1].eval())
        # 训练识别程序
        for i in range(3000):
            sess.run(train_op)
            print('训练第{}次，准确率为：{}'.format(i, sess.run(accuracy)))
        saver.save(sess, './ckpt/captcha_model')

        # 回收线程
        coord.request_stop()
        coord.join(threads)

    return None


if __name__ == '__main__':
    with tf.Session() as sess:
        read_data()
