import time
import sys
import tensorflow as tf
import numpy as np
from tqdm import tqdm
import rnn_crbm
import input_manipulation

"""
    This file contains the code for training the RNN-RBM by using the data in the Pop_Music_Midi directory
"""


batch_size = 100 #The number of trianing examples to feed into the rnn_rbm at a time
epochs_to_save = 5 #The number of epochs to run between saving each checkpoint
saved_weights_path = "parameter_checkpoints/initialized.ckpt" #The path to the initialized weights checkpoint file

def main(num_epochs):
    #First, we build the model and get pointers to the model parameters
    xt, utm1, cost, W, bh, bv, lr, Wuh, Wuv, Wvu, Wuu, bu, u0 = rnn_crbm.rnncrbm()

    #The trainable variables include the weights and biases of the RNN and the RBM, as well as the initial state of the RNN
    tvars = [W, Wuh, Wuv, Wvu, Wuu, bh, bv, bu]
    # opt_func = tf.train.AdamOptimizer(learning_rate=lr)
    # grads, _ = tf.clip_by_global_norm(tf.gradients(cost, tvars), 1)
    # updt = opt_func.apply_gradients(zip(grads, tvars))

    #The learning rate of the  optimizer is a parameter that we set on a schedule during training
    opt_func = tf.train.GradientDescentOptimizer(learning_rate=lr)
    gvs = opt_func.compute_gradients(cost, tvars)
    def ClipIfNotNone(grad):
        if grad is None:
            return grad
        return tf.clip_by_value(grad, -10., 10.)

    gvs = [(ClipIfNotNone(grad), var) for grad, var in gvs]
    updt = opt_func.apply_gradients(gvs)#The update step involves applying the clipped gradients to the model parameters

    songs = input_manipulation.get_songs('Game_Music_Midi') #Load the songs

    saver = tf.train.Saver(tvars) #We use this saver object to restore the weights of the model and save the weights every few epochs
    with tf.Session() as sess:
        init = tf.global_variables_initializer()
        sess.run(init)
        saver.restore(sess, saved_weights_path) #Here we load the initial weights of the model that we created with weight_initializations.py

        #We run through all of the songs n_epoch times
        print ("starting")
        for epoch in range(num_epochs):
            costs = []
            start = time.time()
            for s_ind, song in enumerate(songs):
                for i in range(song.shape[0]):
                    tr_x = song[i,:,:]
                    alpha = 0.0001 #We decrease the learning rate according to a schedule.
                    _, C = sess.run([updt, cost], feed_dict={xt: tr_x, lr: alpha})
                    costs.append(C)
            #Print the progress at epoch
            print ("epoch: {} cost: {} time: {}".format(epoch, np.mean(costs), time.time()-start))
            print
            #Here we save the weights of the model every few epochs
            if (epoch + 1) % epochs_to_save == 0:
                saver.save(sess, "parameter_checkpoints/epoch_{}.ckpt".format(epoch))

if __name__ == "__main__":
    main(int(sys.argv[1]))
