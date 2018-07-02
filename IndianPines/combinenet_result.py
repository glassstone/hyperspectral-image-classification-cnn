#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 16 23:21:24 2018

@author: ssw
"""

import tensorflow as tf
import os
import scipy.io
from next_batch_for_combinenet import Dataset_for_combinenet
import numpy as np
import result_eval

DATA_PATH = "/home/ssw/Hyperspectral_classification_CNN/v4/Data"
data_filename = 'Indianpines_test_feature.mat'

eval_data_1d = scipy.io.loadmat(os.path.join(DATA_PATH, data_filename))['test_feature_1d']
eval_data_2d = scipy.io.loadmat(os.path.join(DATA_PATH, data_filename))['test_feature_2d']
eval_labels = scipy.io.loadmat(os.path.join(DATA_PATH, data_filename))['test_labels']

eval_data = np.hstack((eval_data_1d, eval_data_2d))
eval_dataset = Dataset_for_combinenet(eval_data, eval_labels)

batch_size_for_test = 1
test_labels = np.argmax(eval_labels, axis=1)
predict_labels=np.zeros(eval_dataset.sample_num, dtype=int)

tf.reset_default_graph()

with tf.Session() as sess:
    #load model
    saver = tf.train.import_meta_graph('./model/direct_combinenet/direct_combinenet-model-20000.meta')
    saver.restore(sess, tf.train.latest_checkpoint("./model/direct_combinenet/"))
    graph = tf.get_default_graph()
    x = graph.get_tensor_by_name("x:0")
    y_ = graph.get_tensor_by_name("y_:0")
    predict_y = graph.get_tensor_by_name("predict_y:0")
    keep_prob = graph.get_tensor_by_name("keep_prob:0")
    for i in range(eval_dataset.sample_num):
        test_batch = eval_dataset.next_batch(batch_size_for_test)
        predict_labels[i]=np.argmax(sess.run(predict_y, feed_dict={
            x: test_batch[0], y_: test_batch[1], keep_prob: 1.0}))

cnf_matrix = result_eval.my_cnf_matrix(test_labels, predict_labels)
kappa = result_eval.my_kappa(test_labels, predict_labels)
oa = result_eval.my_oa(test_labels, predict_labels)
(accuracy, aa) = result_eval.my_aa(cnf_matrix)