import tensorflow as tf
import os
import numpy as np
from scripts import cloud_loader
from scripts import pointnet_wrapper
import sys

print "1"
print len([v for v in tf.global_variables()])

tf.reset_default_graph()


print "2"
print len([v for v in tf.global_variables()])

os.chdir(os.path.dirname(os.path.realpath(__file__)))


custom_op = ["/workspace/scripts/PointNet2/tf_ops/3d_interpolation/tf_interpolate_so.so",
            "/workspace/scripts/PointNet2/tf_ops/3d_interpolation/zero_out.so",
            "/workspace/scripts/PointNet2/tf_ops/grouping/tf_grouping_so.so",
            "/workspace/scripts/PointNet2/tf_ops/sampling/tf_sampling_so.so" ]

loaded_op = [tf.load_op_library(op) for op in custom_op]    

num_cores = 4
batch_size = 16

print "line23"
print len([v for v in tf.global_variables()])

test_data_path = [i.tolist() for i in np.load("/workspace/scripts/test_data_path.npy", allow_pickle=True)]

test_labels = [i.tolist() for i in np.load("/workspace/scripts/test_label.npy", allow_pickle=True)]

os.chdir("/workspace/data/")
test_data_paths = [paths_and_handpose[:2] for paths_and_handpose in test_data_path]

test_cloud_indices = [paths_and_handpose[3:5] for paths_and_handpose in test_data_path]


test_handposes_float = [[float(i) for i in paths_and_handpose[2].split(' ')] for paths_and_handpose in test_data_path]

# Here!
test_path_label_ds = tf.data.Dataset.from_tensor_slices((test_data_paths[:batch_size], test_handposes_float[:batch_size], test_cloud_indices[:batch_size], test_labels[:batch_size]))


cloud_loader = cloud_loader.CloudLoader(1024, 3)

test_ds = test_path_label_ds.map(cloud_loader.load_and_preprocess_cloud_from_path_label, num_parallel_calls=num_cores)

test_ds = test_ds.batch(batch_size).prefetch(25)


test_iter = tf.data.Iterator.from_structure(test_ds.output_types, test_ds.output_shapes)
next_test_element = test_iter.get_next()
test_init_op = test_iter.make_initializer(test_ds)

learning_rate = 0.0001
decay_step = 200000
decay_rate = 0.7
bn_init_decay = 0.5
bn_decay_decay_step = float(decay_step)
bn_decay_decay_rate = 0.5
bn_decay_clip = 0.99

print "3"
print len([v for v in tf.global_variables()])

net = pointnet_wrapper.PointNet(batch_size, 1024, 3, learning_rate, decay_step, decay_rate, \
bn_init_decay, bn_decay_decay_step, bn_decay_decay_rate, bn_decay_clip, num_labels=5)

print "4"
print len([v for v in tf.global_variables()])


session =  tf.Session() 

print "5"
print len([v for v in tf.global_variables()])

init = tf.global_variables_initializer()
session.run(init)

print "6"
print len([v for v in tf.global_variables()])

session.run(test_init_op)

print "7"
print len([v for v in tf.global_variables()])
print [v for v in tf.global_variables()]
saver = tf.train.import_meta_graph("/workspace/output/2021_11_04_14_50_53/tf_model_epoch_35.meta")
saver.restore(session, tf.train.latest_checkpoint("/workspace/output/2021_11_04_14_50_53/"))

print "8"
print len([v for v in tf.global_variables()])

data, labels = session.run(next_test_element)

graph = tf.get_default_graph()                                          

"""
Note:
graph = tf.get_default_graph()
ops = [op for op in graph.get_operations()]
"""
out = graph.get_tensor_by_name('fc6/Relu:0')

feed_dict = {graph.get_tensor_by_name('Placeholder:0'): data,
            graph.get_tensor_by_name('Placeholder_2:0'): False}

pred = session.run([out], feed_dict=feed_dict)

print pred


# feed_dict = {net.ops['pointclouds_pl']: data,
# net.ops['labels_pl']: labels,
# net.ops['is_training_pl']: False}



# step, loss_val, pred_val, softmax_out = session.run([
# net.ops['step'],
# net.ops['loss'],
# net.ops['pred'],
# net.ops['softmax']], feed_dict=feed_dict)