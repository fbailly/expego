#!/usr/bin/env python
import sys
import os
import csv
import numpy as np
import scipy as sp
from IPython import embed
import matplotlib.pyplot as plt
import matplotlib as mpl

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

