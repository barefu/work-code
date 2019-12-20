import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_integer('is_train', 1, '指定程序是否预测')


def full_connected():
    # 获取mnist数据
    mnist = input_data.read_data_sets('./file/', one_hot=True)

    # 1、建立数据的占位符x:[None, 784] y_ture[None, 10]
    with tf.variable_scope('data'):
        x = tf.placeholder(tf.float32, [None, 784])
        
        y_ture = tf.placeholder(tf.int32, [None, 10])

    # 2、建立一个全连接层的神经网络 w [784, 10]  b [10]
    with tf.variable_scope('fc_model'):
        # 随机初始化权重和偏置
        weight = tf.Variable(tf.random_normal([784, 10], mean=0.0, stddev=1.0), name='w')
        bias = tf.Variable(tf.constant(0.0, shape=[10]))
        # 预测None个样本的输出结果[None, 784] *[784, 10] + [10] = [None, 10]
        y_predict = tf.matmul(x, weight) + bias

    # 3、求出所有样本的损失值，然后求平均值
    with tf.variable_scope('soft_cross'):

        # 求平均交叉熵损失值
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_ture, logits=y_predict))

    # 4、梯度下降求出损失
    with tf.variable_scope('optimizer'):

        train_op = tf.train.GradientDescentOptimizer(0.1).minimize(loss)

    # 5、计算准确率   argmax(值列表， [axis])
    with tf.variable_scope('acc'):
        equal_list = tf.equal(tf.argmax(y_ture, 1), tf.argmax(y_predict, 1))
        # equai_list  [1,1,0,1,0,1,1,1,1,1,0]
        accuracy = tf.reduce_mean(tf.cast(equal_list, tf.float32))

    # 收集变量
    tf.summary.scalar('losses', loss)
    tf.summary.scalar('acc', accuracy)

    tf.summary.histogram('weights', weight)
    tf.summary.histogram('biases', bias)

    # 定义初始化变量op
    init_op = tf.global_variables_initializer()

    # 定义一个合并变量的op
    merged = tf.summary.merge_all()

    # 创建一个saver
    saver = tf.train.Saver()

    # 6、开启回话训练
    with tf.compat.v1.Session() as sess:
        #初始化变量
        sess.run(init_op)

        # 建立events文件，写入事件
        filewriter = tf.summary.FileWriter('./board/', graph=sess.graph)

        if FLAGS.is_train == 1:

            # 循环步数去训练， 更新参数预测
            for i in range(5000):
                # 取出特征值目标值
                mnist_x, mnist_y = mnist.train.next_batch(50)

                # 运行train_op训练
                sess.run(train_op, feed_dict={x: mnist_x, y_ture: mnist_y})

                # 写入每次训练的值
                summary = sess.run(merged, feed_dict={x: mnist_x, y_ture: mnist_y})
                filewriter.add_summary(summary, i)

                print('训练第{}次，准确率为：{}'.format(i, sess.run(accuracy, feed_dict={x: mnist_x, y_ture: mnist_y})))

            # 保存模型
            saver.save(sess, './ckpt/fc_model')
        else:
            # 加载模型
            saver.restore(sess, './ckpt/fc_model')

            # 如果是0，预测
            for i in range(100):
                x_test, y_text = mnist.test.next_batch(1)
                print('第{}张图片，手写数字是：{}， 预测结果是：{}'.format(i, tf.argmax(y_text, 1).eval()
                                                         , tf.argmax(sess.run(y_predict, feed_dict={x: x_test, y_ture: y_text}), 1).eval()))

    return None


if __name__ == '__main__':
    full_connected()
