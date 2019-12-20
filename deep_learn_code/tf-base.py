import tensorflow as tf
import os
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 实现一个加法运算

# a = tf.constant(5.0)
# b = tf.constant(6.0)
# tf.get_default_graph()
# print(a, b)
# sum1 = tf.add(a, b)
var = tf.Variable(tf.random_normal([2, 3], mean=0.0, stddev=1.0))
init_op = tf.global_variables_initializer()
with tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(log_device_placement=True)) as sess:
    sess.run(init_op)
    # filewriter = tf.summary.FileWriter('D:\\work-content\\tf_study\\board', graph=sum1.graph)
    print(sess.run(var))

