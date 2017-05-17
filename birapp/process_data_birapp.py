#!/usr/bin/env python
import sys
import os
import csv
import numpy as np
import scipy as sp
import pickle
from scipy import signal
from IPython import embed
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from extract_point import points_extract_pos_s
from extract_copl import extract_coplanarity_ls
from dic_gestion import *
from data_filters import *
from data_check import *
from data_process import *
from data_stats import *



def main(argv) :
	PI_list = ['Bassin','ChevilleD', 'ChevilleG', 'CoudeG', 'EpauleD', 'EpauleG', 'GenouxD', 'GenouxG', 'PoignetG', 'Tete']
	np.set_printoptions(linewidth=150,precision=4)
	nb_sb,nb_PI = get_numbers()
	realbirapp1 = 2./10./(3./5.)
	realbirapp2 = 2./10./(5./3.)
	#~ viseur_filt, viseur_speed_pb = viseur_filter(viseur)
	#~ points_extract_speed(viseur_speed_pb)
	#~ points_extract_pos(viseur_filt,viseur_speed_pb)
	#~ results_dic = add_subject_to_results('galo',results_dic)
	#~ massive_check('galo')
	# Pour regarder chaque essai d'un sujet :
	#~ label_trials('flo')
	results_dic = build_results_dic()
	save_dic(results_dic,'results_dic')
	results_dic = load_dic('results_dic')
	birapp_table_1,birapp_table_2,birapp_table_3,col_table_1,col_table_2,col_table_3, subjects_list,PI_list = build_result_table(results_dic,nb_sb,nb_PI,PI_list) 
	birapp_table_exc_1,birapp_table_exc_2 = export_stats(birapp_table_1,birapp_table_2,subjects_list,PI_list,nb_sb,nb_PI)
	embed()
if __name__ == '__main__':
	main(sys.argv)
