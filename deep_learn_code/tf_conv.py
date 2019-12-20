import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data


# 定义初始化权重的函数
def weight_variables(shape):
    w = tf.Variable(tf.random_normal(shape=shape, mean=0.0, stddev=1.0))
    return w


# 定义初始化偏置的函数
def bbias_variables(shape):
    b = tf.Variable(tf.random_normal(shape=shape, mean=0.0, stddev=1.0))
    return b


def model():
    """
    自定义卷积模型
    :return:
    """
    # 1、准备数据占位符 x[None, 784], y_ture [None, 10]
    with tf.variable_scope('data'):
        x = tf.placeholder(tf.float32, [None, 784])
        y_ture = tf.placeholder(tf.int32, [None, 10])

    # 2、一卷积层、卷积：5*5*1，32个，1步  、激活、池化
    with tf.variable_scope('conv1'):
        # 初始化权重
        w_1 = weight_variables([5, 5, 1, 32])
        # 初始化偏置
        b_1 = bbias_variables([32])
        # 对x形状改变[None, 784] ---> [None, 28, 28, 1]
        x_reshape = tf.reshape(x, [-1, 28, 28, 1])
        # [None,28,28,1]  ---> [None, 28,28,1]
        x_relu1 = tf.nn.relu(tf.nn.conv2d(x_reshape, w_1, strides=[1, 1, 1, 1], padding='SAME') + b_1)
        # 池化 2*2， strides 2 [None,28,28,32]  --->[None, 14,14,32]
        x_pool1 = tf.nn.max_pool(x_relu1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

    # 3、二卷积层 卷积：5*5*32，64个，1步  、激活、池化
    with tf.variable_scope('conv2'):
        # 初始化权重
        w_2 = weight_variables([5, 5, 32, 64])
        # 初始化偏置
        b_2 = bbias_variables([64])
        #     卷积、激活、池化
        x_relu2 = tf.nn.relu(tf.nn.conv2d(x_pool1, w_2, strides=[1, 1, 1, 1], padding='SAME') + b_2)
        # 池化 2*2， strides 2 [None,14,14,64]  --->[None, 7,7,64]
        x_pool2 = tf.nn.max_pool(x_relu2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

    # 4、全连接层[None , 7, 7, 64]--->[None, 7*7*64]*[7*7*64, 10] + [10] = [None, 10]
    with tf.variable_scope('conv2'):
        w_fc = weight_variables([7 * 7 * 64, 10])
        b_fc = weight_variables([10])

        # 修改shape
        x_fc_reshape = tf.reshape(x_pool2, [-1, 7*7*64])

        # 进行矩阵运算得出每个样本的10个结果
        y_predict = tf.matmul(x_fc_reshape, w_fc) + b_fc

    return x, y_ture, y_predict


def conv_fc():
    # 获取mnist数据
    mnist = input_data.read_data_sets('./file/', one_hot=True)

    # 定义模型，得出输出
    x, y_ture, y_predict = model()
    # 进行交叉熵损失计算
    # 3、求出所有样本的损失值，然后求平均值
    with tf.variable_scope('soft_cross'):
        # 求平均交叉熵损失值
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_ture, logits=y_predict))

    # 4、梯度下降求出损失
    with tf.variable_scope('optimizer'):
        train_op = tf.train.GradientDescentOptimizer(0.0001).minimize(loss)

    # 5、计算准确率   argmax(值列表， [axis])
    with tf.variable_scope('acc'):
        equal_list = tf.equal(tf.argmax(y_ture, 1), tf.argmax(y_predict, 1))
        # equai_list  [1,1,0,1,0,1,1,1,1,1,0]
        accuracy = tf.reduce_mean(tf.cast(equal_list, tf.float32))

    init_op = tf.global_variables_initializer()
    # 开启回话运行
    with tf.compat.v1.Session() as sess:
        sess.run(init_op)

        for i in range(5000):
            # 取出特征值目标值
            mnist_x, mnist_y = mnist.train.next_batch(50)

            # 运行train_op训练
            sess.run(train_op, feed_dict={x: mnist_x, y_ture: mnist_y})

            print('训练第{}次，准确率为：{}'.format(i, sess.run(accuracy, feed_dict={x: mnist_x, y_ture: mnist_y})))
            # print('真实值：{}， 预测值：{}'.format(tf.argmax(mnist_x, 1).eval(), tf.argmax(sess.run(y_predict, feed_dict={x: mnist_x, y_ture: mnist_y}), 1).eval()))

    return None


if __name__ == '__main__':
    conv_fc()
