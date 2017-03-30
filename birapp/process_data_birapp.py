#!/usr/bin/env python
import sys
import os
import csv
import numpy as np
import scipy as sp
from scipy import signal
from IPython import embed
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
from scipy.cluster.vq import kmeans
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
	
def PI_filter(datafile) :
	plotflag = 0
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
		fig = plt.figure()
		ax = fig.gca(projection='3d')
		ax.plot(PIx, PIy, PIz, label='PI pos')
		ax.plot(PIx_f, PIy_f, PIz_f, label='PI pos')
		ax.legend()
		ax.scatter(PIx_f_med, PIy_f_med, PIz_f_med, label='PI pos',color='green')
		plt.show()
	PI_med = np.array([PIx_f_med,PIy_f_med,PIz_f_med])
	return PI_med

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
	embed()
	return

def points_extract_pos(viseur_filt,viseur_speed) :
	# cluster 3D position
	Nkmean = 8
	est = KMeans(n_clusters=Nkmean)
	est.fit(viseur_filt)
	labels = est.labels_
	fig = plt.figure(1,figsize=(4,3))
	plt.clf()
	ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)
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
	idx_pos = idx_labels_sorted[0:4]
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
	for vis in [vis1,vis2,vis3,vis4] :
		if not vis.shape[0] %2 :
			np.append(vis,np.array([[10000,10000,10000]]),axis=0)
		med_vis[i,0] = vis[:,0][len(vis[:,0])//2]
		med_vis[i,1] = vis[:,1][len(vis[:,1])//2]
		med_vis[i,2] = vis[:,2][len(vis[:,2])//2]
		# check speed at estimated points
		med_speed[i] = speeds[i][len(speeds[i])//2]
		# display estimates of viseur positions
		ax.scatter(med_vis[i,0],med_vis[i,1],med_vis[i,2],color=dots_colors[i],s=200)
		i += 1
	

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
	plt.show()

def massive_check(subject) :	
	directory = '~/expego/birrap/databirapp/'+subject+'/'
	directory = os.path.expanduser(directory)
	viseur_file = 'viseur.csv'
	for filename in os.listdir(directory):
			PI_directory = directory+filename
			if os.path.isdir(PI_directory) :
				for session in ['1','2'] :
					try :
					file_directory = PI_directory + '/' + session + '/' + viseur_file
					print(file_directory)
					viseur = mocap_extract(file_directory)
					viseur_filt, viseur_speed_pb = viseur_filter(viseur)
					points_extract_pos(viseur_filt,viseur_speed_pb)
					except :
						pass
					
					
def main(argv) :
	directory = '~/expego/birrap/databirapp/kevin/EpauleD/1/PI.csv'
	directory = os.path.expanduser(directory)
	PI = mocap_extract(directory)
	directory = '~/expego/birrap/databirapp/kevin/Tete/2/viseur.csv'
	directory = os.path.expanduser(directory)
	viseur = mocap_extract(directory)
	#~ viseur_animation(viseur)
	#~ viseur_filt, viseur_speed_pb = viseur_filter(viseur)
	#~ points_extract_speed(viseur_speed_pb)
	#~ points_extract_pos(viseur_filt,viseur_speed_pb)
	massive_check('flo')
	
if __name__ == '__main__':
	main(sys.argv)
