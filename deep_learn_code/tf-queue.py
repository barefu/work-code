import tensorflow as tf

# 模拟同步先处理数据，后取数据训练

# 1、首先定义队列
Q = tf.queue.FIFOQueue(3, tf.float32)

# 放入数据
enq_many = Q.enqueue_many([[0.1, 0.2, 0.3], ])

# 2、定义读取数据，+1，再放入队列
out_q = Q.dequeue()
data = out_q + 1
en_q = Q.enqueue(data)

with tf.compat.v1.Session() as sess:
    # 初始化队列
    sess.run(enq_many)

    # 处理数据
    for i in range(100):
        sess.run(en_q)

    # 训练数据
    for i in range(Q.size().eval()):
        print(sess.run(Q.dequeue()))