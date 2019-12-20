import tensorflow as tf


# 模拟一步处理数据的过程
# 1、定义队列，指定1000
Q = tf.queue.FIFOQueue(1000, tf.float32)
# 2、定义子线程  循环取值 +1 放入队列
var = tf.Variable(0.0)
# 实现变量自增  tf.assign_add
data = tf.assign_add(var, tf.constant(1.0))
en_q = Q.enqueue(data)
# 3、定义队列管理器op，指定子线程该做的工作
qr = tf.train.QueueRunner(Q, enqueue_ops=[en_q] * 2)

# 初始化变量op
init_op = tf.global_variables_initializer()

with tf.compat.v1.Session() as sess:
    # 初始化变量
    sess.run(init_op)

    # 开启线程管理器
    coord = tf.train.Coordinator()

    # 真正开启子线程
    threads = qr.create_threads(sess, coord=coord, start=True)

    # 主线程，不断读取数据训练
    for i in range(300):
        print(sess.run(Q.dequeue()))

    # 回收
    coord.request_stop()
    coord.join(threads)

