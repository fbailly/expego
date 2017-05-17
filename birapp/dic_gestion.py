#!/usr/bin/env python
import sys
import os
import csv
import numpy as np
import scipy as sp
from IPython import embed
import matplotlib.pyplot as plt
import matplotlib as mpl

def add_subject_to_results(subject,results_dic) :
	results_dic[subject] = {}
	directory = '~/expego/birapp/databirapp/'+subject+'/'
	directory = os.path.expanduser(directory)
	print(directory)
	viseur_file = 'viseur.csv'
	PI_file = 'PI.csv'
	for filename in os.listdir(directory):
			results_dic[subject][filename] = {}
			PI_directory = directory+filename
			if os.path.isdir(PI_directory) :
				for session in ['1','2','3'] :
					try :
						results_dic[subject][filename][session] = {}
						viseur_file_directory = PI_directory + '/' + session + '/' + viseur_file
						PI_file_directory = PI_directory + '/' + session + '/' + PI_file
						print(viseur_file_directory)
						print(PI_file_directory)
						viseur = mocap_extract(viseur_file_directory)
						PI = mocap_extract(PI_file_directory)
						viseur_filt, viseur_speed_pb = viseur_filter(viseur)
						nkmean_session = read_nkmean(subject,filename,session)
						ax,med_vis = points_extract_pos_s(viseur_filt,viseur_speed_pb,int(nkmean_session),0)
						ax, med_PI = 	PI_filter(PI,ax)
						results_dic[subject][filename][session]['viseur'] = med_vis
						results_dic[subject][filename][session]['PI'] = med_PI
					except :
						print(PI_directory + '-------------------->*******FAILED********')
	return results_dic
		
def build_results_dic() :
	results_dic = {}
	directory = '~/expego/birapp/databirapp/'
	directory = os.path.expanduser(directory)
	for subjects in os.listdir(directory) :
		if os.path.isdir(directory+subjects) :
			add_subject_to_results(subjects,results_dic)
	return results_dic
	
def save_dic(dic,filedic) :
	with open(filedic+'.pickle', 'wb') as handle:
		pickle.dump(dic, handle, protocol=pickle.HIGHEST_PROTOCOL)
		
def load_dic(filedic) :
	with open(filedic+'.pickle', 'rb') as handle:
		dic = pickle.load(handle)
	return dic	
