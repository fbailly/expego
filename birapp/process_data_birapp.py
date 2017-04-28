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

def mocap_extract(filename) :
	with open(filename, 'rb') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		datafile = list(spamreader)
		datafile = datafile[3::]
		datafile = np.array(datafile)
		datafile = np.delete(datafile,7,1)
		datafile = datafile.astype(np.float)
	return datafile
	
def PI_filter(datafile,ax) :
	plotflag = 1
	PIx = datafile[:,0]
	PIy = datafile[:,1]
	PIz = datafile[:,2]

	PIx_f = signal.medfilt(PIx,21)
	PIy_f = signal.medfilt(PIy,21)
	PIz_f = signal.medfilt(PIz,21)
	PIx_f_med = np.median(PIx_f)
	PIy_f_med = np.median(PIy_f)
	PIz_f_med = np.median(PIz_f)
	if plotflag :
		ax.plot(PIx, PIy, PIz, label='PI pos')
		ax.plot(PIx_f, PIy_f, PIz_f, label='PI pos')
		ax.legend()
		ax.scatter(PIx_f_med, PIy_f_med, PIz_f_med, label='PI pos',color='green',s=200)
	PI_med = np.array([PIx_f_med,PIy_f_med,PIz_f_med])
	return ax,PI_med

def pb_signal(data) :
	P=7
	h = signal.firwin(numtaps=2*P+1,cutoff=[0.1],nyq=0.5,window='hann')
	data_pb = signal.convolve(data,h,mode='valid')
	return data_pb

def diff_signal(data) :
	fe = 120.0
	te=1.0/fe
	data_pb = pb_signal(data)
	a=[te]
	b=[1,-1]
	data_diff = signal.lfilter(b,a,data_pb)
	return data_diff
	
def viseur_filter(datafile) :
	plotflag = 0
	viseurx = datafile[:,0]
	viseury = datafile[:,1]
	viseurz = datafile[:,2]
	viseur_start = np.array([viseurx[0],viseury[1],viseurz[2]])
	viseurx_pb = pb_signal(viseurx)
	viseury_pb = pb_signal(viseury)
	viseurz_pb = pb_signal(viseurz)
	viseurx_diff = 	diff_signal(viseurx)
	viseury_diff = 	diff_signal(viseury)
	viseurz_diff = 	diff_signal(viseurz) 
	viseur_speed = np.sqrt(pow(viseurx_diff,2)+pow(viseury_diff,2)+pow(viseurz_diff,2))
	viseur_speed_pb = pb_signal(viseur_speed)
	viseur_speed_med = signal.medfilt(viseur_speed,21)
	viseur_speed_med_pb = pb_signal(viseur_speed_med)
	viseur_filt = np.array([viseurx_pb,viseury_pb,viseurz_pb]).T
	

	if plotflag :
		fig1 = plt.figure()
		ax1 = fig1.gca()
		ax11 = fig1.add_subplot(411) 
		ax11.plot(viseur_speed_pb)
		ax11 = fig1.add_subplot(412) 
		ax11.plot(viseurx)
		ax12 = fig1.add_subplot(413)
		ax12.plot(viseury)
		ax13 = fig1.add_subplot(414)
		ax13.plot(viseurz)
		plt.show()
		fig2 = plt.figure()
		ax2 = fig2.gca(projection='3d')
		ax2.plot(viseurx, viseury, viseurz, label='Viseur pos')
		ax2.plot(viseurx_pb, viseury_pb, viseurz_pb, label='Viseur pos filtered')
		ax2.legend()
		ax2.scatter(viseur_start[0], viseur_start[1], viseur_start[2], label='Start',color='red')
		plt.show()
		
	return viseur_filt, viseur_speed_med_pb
	
def viseur_animation(datafile) :
	viseurx = datafile[:,0]
	viseury = datafile[:,1]
	viseurz = datafile[:,2]
	viseurx_pb = pb_signal(viseurx)
	viseury_pb = pb_signal(viseury)
	viseurz_pb = pb_signal(viseurz)
	k = 0
	plt.ion()
	fig = plt.figure()
	ax2 = fig.gca(projection='3d')
	ax2.plot(viseurx, viseury, viseurz, label='Viseur pos')
	ax2.plot(viseurx_pb, viseury_pb, viseurz_pb, label='Viseur pos filtered')
	ax2.legend()
	ax2.scatter(viseurx[k], viseury[k], viseurz[k], label='Current',color='red')
	for k in range(0,len(viseurx),10) :
		ax2.scatter(viseurx[k], viseury[k], viseurz[k], label='Current',color='red')
		plt.pause(0.1)
		
def points_extract_speed(viseur_speed_pb) :
	# find zero speed slots
	Nkmean = 3
	viseur_speed_pb = np.exp(viseur_speed_pb)
	km = kmeans(viseur_speed_pb,Nkmean)
	couleurs = [ 'g', 'r', 'c', 'm', 'y', 'k'] * 10 #why not?
	i=0
	moys_sorted = np.sort(km[0])
	for moy in moys_sorted:
		i+=1
		couleurs = [ 'g', 'r', 'c', 'm', 'y', 'k'] * 10 #why not?
		plt.axhline(y=moy, color=couleurs[i], linestyle='-')
	thresh = (moys_sorted[0]+moys_sorted[1])/2.
	low_speed = (viseur_speed_pb<thresh)+0
	low_speed_int = np.diff(low_speed)
	nb_int = 0
	old_speed = 0
	for k in range(len(low_speed)) :
		if (low_speed[k] == 1) and (old_speed != 1) :
			nb_int +=1
		old_speed = low_speed[k]
	plt.plot(low_speed)
	plt.title('Nombre d intervalles = {0}'.format(nb_int))
	plt.plot(viseur_speed_pb)
	plt.show()
	return

def points_extract_pos(viseur_filt,viseur_speed,Nkmean,plt_flag) :
	# cluster 3D position
	#~ Nkmean = 8
	est = KMeans(n_clusters=Nkmean)
	est.fit(viseur_filt)
	labels = est.labels_
	fig = plt.figure(1,figsize=(4,3))
	ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)
	if plt_flag == True :
		#~ plt.clf()
		ax.scatter(viseur_filt[:, 0], viseur_filt[:, 1], viseur_filt[:, 2], c=labels.astype(np.float))
		ax.w_xaxis.set_ticklabels([])
		ax.w_yaxis.set_ticklabels([])
		ax.w_zaxis.set_ticklabels([])
		ax.set_xlabel('X')
		ax.set_ylabel('Y')
		ax.set_zlabel('Z')
	cnt_labels = np.zeros((Nkmean))
	for i in range(Nkmean) :
		nb_labels_i = sum(labels == i)
		cnt_labels[i] = nb_labels_i
	idx_labels_sorted = np.argsort(cnt_labels)
	idx_labels_sorted = idx_labels_sorted[::-1]
	idx_pos_unsorted = idx_labels_sorted[0:4]
	# reorganizing idx_pos so that it is in order of pointing
	idx_order = np.zeros(4)
	for i in range(4) :
		list_i = np.where(labels==idx_pos_unsorted[i])
		idx_order[i] = list_i[0][len(list_i[0])//2]
	idx_order_sorted = np.argsort(idx_order)
	idx_pos = idx_pos_unsorted[idx_order_sorted]
	# extract the four viseur areas
	vis1 = viseur_filt[labels==idx_pos[0],:]
	vis2 = viseur_filt[labels==idx_pos[1],:]
	vis3 = viseur_filt[labels==idx_pos[2],:]
	vis4 = viseur_filt[labels==idx_pos[3],:]
	offset_derivative = viseur_filt.shape[0]-viseur_speed.shape[0]
	labels_truncated = labels[7:-7]
	vis1speed = viseur_speed[(labels_truncated==idx_pos[0]) ]
	vis2speed = viseur_speed[(labels_truncated==idx_pos[1]) ]
	vis3speed = viseur_speed[(labels_truncated==idx_pos[2]) ]
	vis4speed = viseur_speed[(labels_truncated==idx_pos[3]) ]
	med_vis = np.zeros((4,3))
	med_speed = np.zeros(4)
	i = 0
	speeds = [vis1speed,vis2speed,vis3speed,vis4speed]
	dots_colors = ['r','c','g','m']
	# *********************************************************************TODO : condition the choice of the labels according to the speed
	for vis in [vis1,vis2,vis3,vis4] :
		if not vis.shape[0] %2 :
			np.append(vis,np.array([[10000,10000,10000]]),axis=0)
		med_vis[i,0] = vis[:,0][len(vis[:,0])//2]
		med_vis[i,1] = vis[:,1][len(vis[:,1])//2]
		med_vis[i,2] = vis[:,2][len(vis[:,2])//2]
		# check speed at estimated points
		med_speed[i] = speeds[i][len(speeds[i])//2]
		# display estimates of viseur positions
		if plt_flag == True :
			ax.scatter(med_vis[i,0],med_vis[i,1],med_vis[i,2],color=dots_colors[i],s=200)
		i += 1
	if plt_flag == True :
		plt.figure()
		plt.subplot(411)
		plt.plot(vis1speed)
		plt.axhline(y=med_speed[0], color='red', linestyle='-')
		plt.subplot(412)
		plt.plot(vis1[:,0])
		plt.axhline(y=med_vis[0,0], color='red', linestyle='-')
		plt.subplot(413)
		plt.plot(vis1[:,1])
		plt.axhline(y=med_vis[0,1], color='red', linestyle='-')
		plt.subplot(414)
		plt.plot(vis1[:,2])
		plt.axhline(y=med_vis[0,2], color='red', linestyle='-')
	return ax, med_vis

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
	ax,med_vis = points_extract_pos(viseur_filt,viseur_speed_pb,int(Nkmean),True)
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
					
def add_subject_to_results(subject,results_dic) :
	results_dic[subject] = {}
	directory = '~/expego/birapp/databirapp/'+subject+'/'
	directory = os.path.expanduser(directory)
	print(directory)
	print('Number of clusters for Kmean algo :')
	Nkmean = raw_input()
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
						ax,med_vis = points_extract_pos(viseur_filt,viseur_speed_pb,int(Nkmean),0)
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
			nkmean_subject = read_nkmean(subjects)
			print('Optimal number of cluster for {0} is {1}'.format(subjects,str(nkmean_subject)))
			add_subject_to_results(subjects,results_dic)
	return results_dic
		
def extract_colinearity(viseur_array,PI_array):
	# colinearity of the targets implies coplanarity of vis1, vis2, vis3, vis4 and PI
	# first check for coplanarity of vis1, vis2, vis3 and PI and then vis1, vis2, vis4 and PI
	vis1 = viseur_array[0,:]
	vis2 = viseur_array[1,:]
	vis3 = viseur_array[2,:]
	vis4 = viseur_array[3,:]
	col1 = np.dot(np.cross((vis2-vis1),(PI_array-vis3)),(vis3-vis1))
	col2 = np.dot(np.cross((vis2-vis1),(PI_array-vis4)),(vis4-vis1))
	tot_col = 1./np.sqrt(col1*col1+col2*col2)
	return tot_col
	
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
	print('Number of clusters for Kmean algo :')
	Nkmean = raw_input()
	labeled_trials.write('Number of culster for Kmean : {0}\n'.format(Nkmean))
	for filename in os.listdir(directory):
			PI_directory = directory+filename
			if os.path.isdir(PI_directory) :
				for session in ['1','2','3'] :
					try :
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
						label_trial = '2'
						while label_trial != '1'and label_trial != '0' :  
							print('Label this trial : 1 = good, 0 = bad :')
							label_trial = raw_input()
						label_line = (filename+','+session+','+'label : '+label_trial+'\n')
						labeled_trials.write(label_line)
						
					except :
						print('An error occured : probably no such file or directory {0}: '.format(PI_directory+'/'+session))
						print('Automatically labeled 0')
						label_line = (filename+','+session+','+'label : 0\n')
						labeled_trials.write(label_line)
						pass 
				labeled_trials.close
				
def read_nkmean(subject) :
	directory = '~/expego/birapp/databirapp/'+subject+'/'
	directory = os.path.expanduser(directory)
	labeled_trials = open(directory+'/labeled_trials.txt','r')
	nkmean_file = labeled_trials.readline()
	nkmean_subject = int(nkmean_file[-2])
	return nkmean_subject
	
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
							tot_col = extract_colinearity(viseur_array,PI_array)
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
					
def save_dic(dic,filedic) :
	with open(filedic+'.pickle', 'wb') as handle:
		pickle.dump(dic, handle, protocol=pickle.HIGHEST_PROTOCOL)
def load_dic(filedic) :
	with open(filedic+'.pickle', 'rb') as handle:
		dic = pickle.load(handle)
	return dic	
	
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
			lines = iter(labeled_trials)
			lines.next() # Skip line.
			for line in lines :
				line_split = line.split(',')
				if line_split[1] == '1' :
					mask_trial_1[i,j] = int(line[-2])
					j += 1
				elif line_split[1] == '2' :
					mask_trial_2[i,k] = int(line[-2])
					k += 1
				elif line_split[1] == '3' :
					mask_trial_3[i,l] = int(line[-2])
					l += 1
				else : print('error split')
			i += 1
	mask_trial_1 = np.where(mask_trial_1==1,mask_trial_1,np.nan)
	mask_trial_2 = np.where(mask_trial_2==1,mask_trial_2,np.nan)
	mask_trial_3 = np.where(mask_trial_3==1,mask_trial_3,np.nan)
	return mask_trial_1,mask_trial_2,mask_trial_3

def export_stats(birapp_table_1,birapp_table_2,subjects_list,PI_list,nb_sb,nb_PI) :
	
	directory = '~/expego/birapp/resultbirapp/'
	directory = os.path.expanduser(directory)
	stats_birapp1 = open(directory+'stats_birapp1.csv','w')
	stats_birapp2 = open(directory+'stats_birapp2.csv','w')
	#~ stats_birapp3 = open(directory+'stats_birapp3.csv','w')
	stats_birapp1.write('Sujet;Condition;Resultat\n')
	stats_birapp2.write('Sujet;Condition;Resultat\n')
	#~ stats_birapp3.write('Sujet;Condition;Resultat\n')
	exclude_subject = ['celine','kevin','dinesh']
	exclude_subject = ['celine','kevin','dinesh']
	subject_idx = range(nb_sb)
	for i in range(len(exclude_subject)) :
		subject_idx.remove(subjects_list.index(exclude_subject[i]))		
	for i in subject_idx :
		for j in range(nb_PI) :
			line_to_write1 = '{0};{1};{2}\n'.format(i+1,PI_list[j],birapp_table_1[i,j])
			line_to_write2 = '{0};{1};{2}\n'.format(i+1,PI_list[j],birapp_table_2[i,j])
			#~ line_to_write3 = '{0};{1};{2}\n'.format(i+1,PI_list[j],birapp_table_3[i,j])
			stats_birapp1.write(line_to_write1)
			stats_birapp2.write(line_to_write2)
			#~ stats_birapp3.write(line_to_write3)
	stats_birapp1.close
	stats_birapp2.close
	#~ stats_birapp3.close
	
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
	#~ label_trials('celine')
	#~ results_dic = build_results_dic()
	#~ save_dic(results_dic,'results_dic')
	results_dic = load_dic('results_dic')
	birapp_table_1,birapp_table_2,birapp_table_3,col_table_1,col_table_2,col_table_3, subjects_list,PI_list = build_result_table(results_dic,nb_sb,nb_PI,PI_list) 
	export_stats(birapp_table_1,birapp_table_2,subjects_list,PI_list,nb_sb,nb_PI)
	embed()
if __name__ == '__main__':
	main(sys.argv)
