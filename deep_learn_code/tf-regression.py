import tensorflow as tf
import os

# 添加权重参数， 损失值等在tensorboard观察的情况 1、收集变量 2、合并变量写入事件文件
# 定义命令行参数
# 1、首先定义有哪些参数需要在运行时指定
# 2、在程序当中获取定义命令行参数

# 第一个参数：名字，默认值，说明
tf.app.flags.FEAULT_integer('max_step', 100, '模型训练的步数')

def myregression():
    """
    自实现一个线性回归预测
    :return: None
    """
    with tf.variable_scope('data'):
        # 1.准备数据, x 特征值 [100, 1]  y 目标值[100]
        x = tf.random_normal([100, 1], mean=1.75, stddev=1.5, name="x_data")

        # 矩阵相乘必须是二维的
        y_ture = tf.matmul(x, [[0.7]]) + 0.8

    with tf.variable_scope('model'):
        # 2.建立线性回归模型   一个特征，一个权重，一个偏置 y = xw + b
        # 随机给一个权重个一个偏置的值，去计算损失，然后在当前状态下优化（梯度下降）
        # 用变量定义参数，才能优化
        # trainable参数：指定这个变量能跟着梯度下降一起优化
        weight = tf.Variable(tf.random_normal([1, 1], mean=0.0, stddev=1.0), name='w', trainable=True)
        bias = tf.Variable(0.0, name='b')

        y_predict = tf.matmul(x, weight) + bias

    with tf.variable_scope('loss'):
        # 3.建立损失函数，军方误差
        loss = tf.reduce_mean(tf.square(y_ture - y_predict))

    with tf.variable_scope('optimizer'):
        # 4、梯度下降优化损失 leaning_rate: 0, 1, 2, 3......
        train_op = tf.train.GradientDescentOptimizer(0.01).minimize(loss)

    # 收集变量
    tf.summary.scalar('loss', loss)
    tf.summary.histogram('weights', weight)
    # 定义合并tensor的op
    merged = tf.summary.merge_all()

    # 定义一个初始化变量的op
    init_op = tf.global_variables_initializer()

    # 定义一个模型保存文件
    saver = tf.train.Saver()

    # 4、通过会话运行程序
    with tf.compat.v1.Session() as sess:
        # 初始化变量
        sess.run(init_op)
        # 打印初始化的参数
        print('随机初始化的参数权重为：{}，偏置为：{}'.format(sess.run(weight), bias.eval()))

        # 建立事件文件
        filewriter = tf.summary.FileWriter('./board', graph=sess.graph)

        # 加载模型，覆盖模型中随机定义的参数，从上次训练的参数加过开始
        if os.path.exists('./ckpt/checkpoint'):
            saver.restore(sess, './ckpt/liner_model')

        # 运行优化op， 循环训练优化
        for i in range(500):
            sess.run(train_op)
            # 运行合并的tensor
            summary = sess.run(merged)
            filewriter.add_summary(summary, i)

            print('第{}次优化的参数权重为：{}，偏置为：{}'.format(i, weight.eval(), bias.eval()))
        saver.save(sess, './ckpt/liner_model')


if __name__ == '__main__':
    myregression()
