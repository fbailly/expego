#!/usr/bin/env python
import sys
import os
import csv
import numpy as np
import scipy as sp
from IPython import embed
import matplotlib.pyplot as plt
import matplotlib as mpl
from data_filters import *
from extract_point import points_extract_pos_s

def get_numbers() :
	directory = '~/expego/birapp/databirapp/'
	directory = os.path.expanduser(directory)
	nb_sb = len(os.listdir(directory))
	for session in ['1','2'] :
		for subjects in os.listdir(directory) :
			if os.path.isdir(directory+subjects) :
				sub_directory = '~/expego/birapp/databirapp/'+subjects+'/'
				sub_directory = os.path.expanduser(sub_directory)
				i = 0
				for filename in os.listdir(sub_directory):	
					if os.path.isdir(sub_directory+filename) :	
						i +=1
		nb_PI = i
	return nb_sb, nb_PI
	
def extract_birapp(viseur_array,PI_array) :
	# computing birapp without taking care of colinearity
	vis1 = viseur_array[0,:]
	vis2 = viseur_array[1,:]
	vis3 = viseur_array[2,:]
	vis4 = viseur_array[3,:]
	PI_vis1 = vis1-PI_array
	PI_vis2 = vis2-PI_array
	PI_vis3 = vis3-PI_array
	PI_vis4 = vis4-PI_array
	PIvis1_PIvis2 = np.arctan2(np.linalg.norm(np.cross(PI_vis1,PI_vis2)),np.dot(PI_vis1,PI_vis2))
	PIvis2_PIvis3 = np.arctan2(np.linalg.norm(np.cross(PI_vis2,PI_vis3)),np.dot(PI_vis2,PI_vis3))
	PIvis3_PIvis4 = np.arctan2(np.linalg.norm(np.cross(PI_vis3,PI_vis4)),np.dot(PI_vis3,PI_vis4))
	PIvis1_PIvis4 = PIvis1_PIvis2+PIvis2_PIvis3+PIvis3_PIvis4
	sin_PIvis1_PIvis2 = np.sin(PIvis1_PIvis2)
	sin_PIvis2_PIvis3 = np.sin(PIvis2_PIvis3)
	sin_PIvis3_PIvis4 = np.sin(PIvis3_PIvis4)
	sin_PIvis1_PIvis4 = np.sin(PIvis1_PIvis4)
	# premiere methode pour calculer le birapport
	sin_PIvis1_PIvis2 = np.sin(np.arctan2(np.linalg.norm(np.cross(PI_vis1,PI_vis2)),np.dot(PI_vis1,PI_vis2)))
	sin_PIvis1_PIvis4 = np.sin(np.arctan2(np.linalg.norm(np.cross(PI_vis1,PI_vis4)),np.dot(PI_vis1,PI_vis4)))
	sin_PIvis2_PIvis3 = np.sin(np.arctan2(np.linalg.norm(np.cross(PI_vis2,PI_vis3)),np.dot(PI_vis2,PI_vis3)))
	sin_PIvis3_PIvis4 = np.sin(np.arctan2(np.linalg.norm(np.cross(PI_vis3,PI_vis4)),np.dot(PI_vis3,PI_vis4)))
	birapp = sin_PIvis1_PIvis2/sin_PIvis1_PIvis4/(sin_PIvis2_PIvis3/sin_PIvis3_PIvis4)
	return birapp
	
def label_trials(subject) :
	directory = '~/expego/birapp/databirapp/'+subject+'/'
	directory = os.path.expanduser(directory)
	labeled_trials = open(directory+'/labeled_trials.txt','w')
	viseur_file = 'viseur.csv'
	PI_file = 'PI.csv'
	print(directory)
	for filename in os.listdir(directory):
			PI_directory = directory+filename
			if os.path.isdir(PI_directory) :
				for session in ['1','2','3'] :
					try :
						kmean_ok = 0
						while not kmean_ok :
							viseur_file_directory = PI_directory + '/' + session + '/' + viseur_file
							PI_file_directory = PI_directory + '/' + session + '/' + PI_file
							print(viseur_file_directory)
							print(PI_file_directory)
							viseur = mocap_extract(viseur_file_directory)
							PI = mocap_extract(PI_file_directory)
							viseur_filt, viseur_speed_pb = viseur_filter(viseur)
							print('Number of clusters for Kmean algo :')
							Nkmean = raw_input()
							ax,med_vis = points_extract_pos_s(viseur_filt,viseur_speed_pb,int(Nkmean),True)
							ax, Pi_med = PI_filter(PI,ax)
							plt.show()
							print('Restart Kmean clustering ? (1, [0])')
							kmean_reset = raw_input()
							if kmean_reset == '1' :
								kmean_ok = 0
							else :
								kmean_ok = 1
								labeled_trials.write('Number of culster for Kmean,{0},'.format(Nkmean))
								label_trial = '2'
								while label_trial != '1'and label_trial != '0' :  
									print('Label this trial : 1 = good, 0 = bad :')
									label_trial = raw_input()
								label_line = (filename+','+session+','+'label,'+label_trial+'\n')
								labeled_trials.write(label_line)
					except :
						print('An error occured : probably no such file or directory {0}: '.format(PI_directory+'/'+session))
						print('Automatically labeled 0')
						labeled_trials.write('Number of culster for Kmean,NA,'.format(Nkmean))
						label_line = (filename+','+session+','+'label,0\n')
						labeled_trials.write(label_line)
						pass 
				labeled_trials.close
				
def read_nkmean(subject,PI,session) :
	directory = '~/expego/birapp/databirapp/'+subject+'/'
	directory = os.path.expanduser(directory)
	labeled_trials = open(directory+'/labeled_trials.txt','r')
	for lines in labeled_trials :
		line_list = lines.split(',')
		if line_list[2]== PI and line_list[3] == session :
			nkmean_session = line_list[1]
	return nkmean_session
	
def print_birapp(results_dic) :
	directory = '~/expego/birapp/databirapp/'
	directory = os.path.expanduser(directory)
	birapp_results_1 = []
	col_results_1 = []
	header_results_1 = []
	birapp_results_2 = []
	col_results_2 = []
	header_results_2 = []
	for session in ['1','2'] :
		for subjects in os.listdir(directory) :
			sub_directory = '~/expego/birapp/databirapp/'+subjects+'/'
			sub_directory = os.path.expanduser(sub_directory)
			for filename in os.listdir(sub_directory):
				try : 
					viseur_array = results_dic[subjects][filename][session]['viseur']
					PI_array = results_dic[subjects][filename][session]['PI']
					tot_col = extract_colinearity(viseur_array,PI_array)
					birapp, realbirapp1, realbirapp2 = extract_birapp(viseur_array,PI_array)
					if int(session) == 1 :
						birapp_results_1 += [birapp]
						col_results_1 += [tot_col]
						header_results_1 += [subjects+' '+filename+' '+session]
					if int(session) == 2 :
						birapp_results_2 += [birapp]
						col_results_2 += [tot_col]
						header_results_2 += [subjects+' '+filename+' '+session]
				except :
					print filename
	return birapp_results_1, col_results_1, header_results_1,birapp_results_2, col_results_2, header_results_2 
	
def build_result_table(results_dic,nb_sb,nb_PI,PI_list) :
	directory = '~/expego/birapp/databirapp/'
	directory = os.path.expanduser(directory)
	birapp_table_1 = np.zeros([nb_sb,nb_PI])
	birapp_table_2 = np.zeros([nb_sb,nb_PI])
	col_table_1 = np.zeros([nb_sb,nb_PI])
	col_table_2 = np.zeros([nb_sb,nb_PI])
	birapp_table_3 = np.zeros([nb_sb,nb_PI])
	col_table_3 = np.zeros([nb_sb,nb_PI])
	for session in ['1','2','3'] :
		i = 0
		subjects_list = []
		for subjects in os.listdir(directory) :
			if os.path.isdir(directory+subjects) :
				subjects_list += [subjects] 
				sub_directory = '~/expego/birapp/databirapp/'+subjects+'/'
				sub_directory = os.path.expanduser(sub_directory)
				j = 0
				for filename in PI_list:
					if os.path.isdir(sub_directory+filename) :
						try :
							viseur_array = results_dic[subjects][filename][session]['viseur']
							PI_array = results_dic[subjects][filename][session]['PI']
							tot_col = extract_coplanarity_ls(viseur_array,PI_array)
							birapp = extract_birapp(viseur_array,PI_array)
							if int(session) == 1 :
								birapp_table_1[i,j] = birapp
								col_table_1[i,j] = tot_col
							if int(session) == 2 :					
								birapp_table_2[i,j] = birapp
								col_table_2[i,j] = tot_col
							if int(session) == 3 :					
								birapp_table_3[i,j] = birapp
								col_table_3[i,j] = tot_col
						except :
							print('error')
							print(filename+subjects+session)
							if int(session) == 1 :
								birapp_table_1[i,j] = np.nan
								col_table_1[i,j] = np.nan
							if int(session) == 2 :					
								birapp_table_2[i,j] = np.nan
								col_table_2[i,j] = np.nan
							if int(session) == 3 :					
								birapp_table_3[i,j] = np.nan
								col_table_3[i,j] = np.nan
						j += 1
				i += 1
	mask_trial_1,mask_trial_2,mask_trial_3 = mask_trial(nb_sb,nb_PI)
	birapp_table_1 = np.multiply(birapp_table_1,mask_trial_1) 
	birapp_table_2 = np.multiply(birapp_table_2,mask_trial_2) 
	col_table_1 = np.multiply(col_table_1,mask_trial_1) 
	col_table_2 = np.multiply(col_table_2,mask_trial_2) 
	birapp_table_3 = np.multiply(birapp_table_3,mask_trial_3) 
	col_table_3 = np.multiply(col_table_3,mask_trial_3) 
	return birapp_table_1,birapp_table_2,birapp_table_3,col_table_1,col_table_2,col_table_3, subjects_list,PI_list
					
def mask_trial(nb_sb,nb_PI) :
	directory = '~/expego/birapp/databirapp/'
	directory = os.path.expanduser(directory)
	mask_trial_1 = np.empty([nb_sb,nb_PI])
	mask_trial_2 = np.empty([nb_sb,nb_PI])
	mask_trial_3 = np.empty([nb_sb,nb_PI])
	i = 0
	for subjects in os.listdir(directory) :
		if os.path.isdir(directory+subjects) :
			sub_directory = directory+subjects+'/'
			labeled_trials = open(sub_directory+'/labeled_trials.txt','r')
			j = 0
			k = 0
			l = 0
			for lines in labeled_trials :
				line_split = lines.split(',')
				embed()
				if line_split[3] == '1' :
					mask_trial_1[i,j] = int(line_split[5][0])
					j += 1
				elif line_split[3] == '2' :
					mask_trial_2[i,k] = int(line_split[5][0])
					k += 1
				elif line_split[3] == '3' :
					mask_trial_3[i,l] = int(line_split[5][0])
					l += 1
				else : print('error split')
			i += 1
	mask_trial_1 = np.where(mask_trial_1==1,mask_trial_1,np.nan)
	mask_trial_2 = np.where(mask_trial_2==1,mask_trial_2,np.nan)
	mask_trial_3 = np.where(mask_trial_3==1,mask_trial_3,np.nan)
	return mask_trial_1,mask_trial_2,mask_trial_3

