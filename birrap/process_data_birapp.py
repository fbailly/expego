#!/usr/bin/env python
import sys
import os
import csv
import numpy as np
import scipy as sp
from scipy import signal
from IPython import embed
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D

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
	
def viseur_filter(datafile) :
	plotflag = 1
	viseurx = datafile[:,0]
	viseury = datafile[:,1]
	viseurz = datafile[:,2]
	viseur_start = np.array([viseurx[0],viseury[1],viseurz[2]])
	viseurx_f = signal.medfilt(viseurx,11)
	viseury_f = signal.medfilt(viseury,11)
	viseurz_f = signal.medfilt(viseurz,11)
	viseurx_f_med = np.median(viseurx_f)
	viseury_f_med = np.median(viseury_f)
	viseurz_f_med = np.median(viseurz_f)
	viseurx_diff = np.diff(viseurx_f)
	viseury_diff = np.diff(viseury_f)
	viseurz_diff = np.diff(viseurz_f) 
	fig1 = plt.figure()
	ax1 = fig1.gca()
	ax1.plot(viseurx_diff)
	ax1.plot(viseury_diff)
	ax1.plot(viseurz_diff)
	ax1.plot(viseurx_f/100.)
	plt.show()
	if plotflag :
		fig2 = plt.figure()
		ax2 = fig2.gca(projection='3d')
		ax2.plot(viseurx, viseury, viseurz, label='Viseur pos')
		ax2.plot(viseurx_f, viseury_f, viseurz_f, label='Viseur pos')
		ax2.legend()
		ax2.scatter(viseur_start[0], viseur_start[1], viseur_start[2], label='Start',color='red')
		plt.show()
	viseur_med = np.array([PIx_f_med,PIy_f_med,PIz_f_med])
	return viseur_med

def main(argv) :
	directory = '~/expego/birrap/databirapp/flo/EpauleD/1/PI.csv'
	directory = os.path.expanduser(directory)
	PI = mocap_extract(directory)
	directory = '~/expego/birrap/databirapp/flo/EpauleD/1/viseur.csv'
	directory = os.path.expanduser(directory)
	viseur = mocap_extract(directory)
	viseur_filter(viseur)
	embed()
				
if __name__ == '__main__':
	main(sys.argv)
