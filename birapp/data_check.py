#!/usr/bin/env python
import sys
import os
import csv
import numpy as np
import scipy as sp
from IPython import embed
import matplotlib.pyplot as plt
import matplotlib as mpl


def specific_check(subject,PI,session) :
	directory = '~/expego/birapp/databirapp/'+subject+'/'
	directory = os.path.expanduser(directory)
	viseur_file = 'viseur.csv'
	PI_file = 'PI.csv'
	PI_directory = directory+PI
	viseur_file_directory = PI_directory + '/' + session + '/' + viseur_file
	PI_file_directory = PI_directory + '/' + session + '/' + PI_file
	print(viseur_file_directory)
	print(PI_file_directory)
	print('Number of clusters for Kmean algo :')
	Nkmean = raw_input()
	viseur = mocap_extract(viseur_file_directory)
	PI = mocap_extract(PI_file_directory)
	viseur_filt, viseur_speed_pb = viseur_filter(viseur)
	ax,med_vis = points_extract_pos_s(viseur_filt,viseur_speed_pb,int(Nkmean),True)
	ax, Pi_med = PI_filter(PI,ax)
	plt.show()

def massive_check(subject) :	
	directory = '~/expego/birapp/databirapp/'+subject+'/'
	directory = os.path.expanduser(directory)
	viseur_file = 'viseur.csv'
	PI_file = 'PI.csv'
	print(directory)
	print('Number of clusters for Kmean algo :')
	Nkmean = raw_input()
	for filename in os.listdir(directory):
			PI_directory = directory+filename
			if os.path.isdir(PI_directory) :
				for session in ['1','2'] :
					#~ try :
						viseur_file_directory = PI_directory + '/' + session + '/' + viseur_file
						PI_file_directory = PI_directory + '/' + session + '/' + PI_file
						print(viseur_file_directory)
						print(PI_file_directory)	
						viseur = mocap_extract(viseur_file_directory)
						PI = mocap_extract(PI_file_directory)
						viseur_filt, viseur_speed_pb = viseur_filter(viseur)
						ax,med_vis = points_extract_pos(viseur_filt,viseur_speed_pb,int(Nkmean),True)
						ax, Pi_med = PI_filter(PI,ax)
						plt.show()
					#~ except :
						pass
					
		
