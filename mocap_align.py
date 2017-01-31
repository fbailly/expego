#!/usr/bin/env python

import numpy as np
import csv
import sys
from IPython import embed
global mes_bplume
global mes_brouge
global mes_bvide
mes_bplume = np.array([-3.6004087458,3.3680321189,1.5372971483])*100
mes_brouge = np.array([-3.6178109599,3.9675009516,1.5314543185])*100
mes_bvide = np.array([-3.6363492807,4.5560661391,1.5339595827])*100
def mocap_extract(filename) :
	with open(filename, 'rb') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		datafile = list(spamreader)
		datafile = datafile[3::]
		datafile = np.array(datafile)
		datafile = np.delete(datafile,7,1)
		datafile = datafile.astype(np.float)
	return datafile

def mocap_align_abs(data1,data2,ball) :
	# Computes positions of viseur and PI in cm
	pos1 = np.array([np.mean(data1[:,0]),np.mean(data1[:,1]),np.mean(data1[:,2])])*100
	pos2 = np.array([np.mean(data2[:,0]),np.mean(data2[:,1]),np.mean(data2[:,2])])*100

	# pos3 for balls board in second room
	#~ pos3 = np.array([-3.6420,5.0994-2.44/2,2.1465-1.22/2])*100
	
	# Computes position of the three balls
	posred = mes_brouge
	posempty = mes_bvide
	posfeather = mes_bplume
	if ball == 'Red' :
		pos3 = posred
	elif ball == 'Feather' :
		pos3 = posfeather
	elif ball == 'Empty' :
		pos3 = posempty
	else :
		return
			
	# Computes the three angles of the triangle
	ang1 = np.rad2deg(np.arccos(np.dot(pos2-pos1,pos3-pos1)/np.linalg.norm(pos2-pos1)/np.linalg.norm(pos3-pos1)))
	ang2 = np.rad2deg(np.arccos(np.dot(pos1-pos2,pos3-pos2)/np.linalg.norm(pos1-pos2)/np.linalg.norm(pos3-pos2)))
	ang3 = np.rad2deg(np.arccos(np.dot(pos1-pos3,pos2-pos3)/np.linalg.norm(pos1-pos3)/np.linalg.norm(pos2-pos3)))
	
	return ang1
	
	
def main() :
	# In order PI viseur cible
	body1 = mocap_extract(sys.argv[1]+'.csv')
	body2 = mocap_extract(sys.argv[2]+'.csv')
	ang = mocap_align_abs(body1,body2,sys.argv[3]) 
	print('Angle erreur : {0}'.format(ang))
	
if __name__ == '__main__':
	main()
		 

