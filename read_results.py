#!/usr/bin/env python

import rospy
import sys
import os
import message_filters
from IPython import embed
import matplotlib.pyplot as plt
import numpy as np
from mocap_align import mocap_extract, mocap_align_abs




def get_subject() :
	print('______\n\nsujet :')
	subject_id = raw_input()
	directory = '~/catkin_ws/src/mocap/data/'+subject_id+'/'
	directory = os.path.expanduser(directory)
	if not ('results.txt' in os.listdir(directory)):
		print('\nresults seems not to be already computed...\n______')
		return
	for filename in os.listdir(directory):
		print(filename+'\n')
	return subject_id
	
def get_PI(subject_id) :
	print('______\n\nPI :')
	PI_id = ''
	directory = '~/catkin_ws/src/mocap/data/'+subject_id+'/'
	directory = os.path.expanduser(directory)
	while PI_id not in os.listdir(directory):
		print('entrer partie du corps\n')
		PI_id = raw_input();
	return PI_id

def display_results(subject_id) :
	
	balls_centersy = [5.0994-2.44/2,5.0994-2.44/2+0.61,5.0994-2.44/2-0.61]
	balls_centersz = [2.1465-1.22/2,2.1465-1.22/2,2.1465-1.22/2]
	plt.plot(balls_centersy[0],balls_centersz[0],'ro',markersize=40)
	plt.plot(balls_centersy[1],balls_centersz[1],'ko',markersize=40)
	plt.plot(balls_centersy[2],balls_centersz[2],'go',markersize=40)
	plt.axis([3,5,1,2])
	pdc = ''
	while pdc not in os.listdir(directory):
		print('entrer partie du corps\n')
		pdc = raw_input();
	for ballsname in os.listdir(directory+'/'+pdc) :
		print(ballsname+'\n')
	balltype = ''
	while balltype not in os.listdir(directory+'/'+pdc):
		print('entrer type de boule\n')
		balltype = raw_input();
		if balltype == 'red' :
			ballnb = 0
			colorflag = 'rx'
		elif balltype == 'empty' :
			ballnb = 1
			colorflag = 'kx'
		elif balltype == 'feather' :
			ballnb = 2
			colorflag = 'gx'
	for sessionname in os.listdir(directory+'/'+pdc+'/'+balltype) :
		print('sessions :')
		print(sessionname+'\n')
	session = ''
	while session not in os.listdir(directory+'/'+pdc+'/'+balltype):
		print('entrer type de session\n')
		session = raw_input();
	result_id = pdc+','+balltype+','+session
	with open(directory+'/results.txt','r') as results :
		for line in results :
			if result_id in  line :
				resultline = line.rsplit(',')
				resultline[-1] = resultline[-1].strip()
				ang = float(resultline[-1])
				print('Angle erreur : {0}'.format(ang))
	body1 = mocap_extract(directory+'/'+pdc+'/'+balltype+'/'+session+'/'+'PI'+'.csv')
	body2 = mocap_extract(directory+'/'+pdc+'/'+balltype+'/'+session+'/'+'viseur'+'.csv')
	dy,dz = mocap_intercept(body1,body2,balltype)
	print('Deviation Y : {0}\nDeviation Z : {1}'.format(dy,dz))
	plt.plot(balls_centersy[ballnb]+dy/100,balls_centersz[ballnb]+dz/100,colorflag,markersize=50)

def display_results_PI (subject_id,PI_id) :
	directory = '~/catkin_ws/src/mocap/data/'+subject_id+'/'
	directory = os.path.expanduser(directory)
	if not ('results.txt' in os.listdir(directory)):
		print('\nresults seems not to be already computed...\n______')
		return
	balls_centersy = [5.0994-2.44/2,5.0994-2.44/2+0.61,5.0994-2.44/2-0.61]
	balls_centersz = [2.1465-1.22/2,2.1465-1.22/2,2.1465-1.22/2]
	plt.plot(balls_centersy[0],balls_centersz[0],'ro',markersize=40)
	plt.plot(balls_centersy[1],balls_centersz[1],'ko',markersize=40)
	plt.plot(balls_centersy[2],balls_centersz[2],'go',markersize=40)
	plt.axis([3,5,1,2])		
	for balltype in os.listdir(directory+'/'+PI_id) :		
		if balltype == 'red' :
			ballnb = 0
			colorflag = 'rx'
		elif balltype == 'empty' :
			ballnb = 1
			colorflag = 'kx'
		elif balltype == 'feather' :
			ballnb = 2
			colorflag = 'gx'
		for sessionname in os.listdir(directory+'/'+PI_id+'/'+balltype) :
			result_id = PI_id+','+balltype+','+sessionname
			print(result_id)
			with open(directory+'/results.txt','r') as results :
				for line in results :
					if result_id in  line :
						resultline = line.rsplit(',')
						resultline[-1] = resultline[-1].strip()
						ang = float(resultline[-1])
						print('Angle erreur : {0}'.format(ang))
						body1 = mocap_extract(directory+'/'+PI_id+'/'+balltype+'/'+sessionname+'/'+'PI'+'.csv')
						body2 = mocap_extract(directory+'/'+PI_id+'/'+balltype+'/'+sessionname+'/'+'viseur'+'.csv')
						dy,dz = mocap_intercept(body1,body2,balltype)
						print('Deviation Y : {0}\nDeviation Z : {1}'.format(dy,dz))
						plt.plot(balls_centersy[ballnb]+dy/100,balls_centersz[ballnb]+dz/100,colorflag,markersize=25)
	
	
def mocap_intercept(data1,data2,ball) :
	# Computes positions of viseur and PI in cm
	pos1 = np.array([np.mean(data1[:,0]),np.mean(data1[:,1]),np.mean(data1[:,2])])*100
	pos2 = np.array([np.mean(data2[:,0]),np.mean(data2[:,1]),np.mean(data2[:,2])])*100

	# pos3 for balls board in second room
	pos3 = np.array([-3.6420,5.0994-2.44/2,2.1465-1.22/2])*100
	
	# Offsets
	#~ pos1 = pos1 - np.array([0.0447,0,1.3750]) # PI offset
	#~ pos2 = pos2 - np.array([0.75,0,1.5]) # Viseur offset
	
	# Computes position of the three balls
	posred = pos3
	posempty = pos3 + np.array([0,61,0])
	posfeather = pos3 - np.array([0,61,0])
	if ball == 'red' :
		pos3 = posred
	elif ball == 'feather' :
		pos3 = posfeather
	elif ball == 'empty' :
		pos3 = posempty
	else :
		return
			
	# Computes the interception
	PI_viseur = pos2-pos1
	PI_viseur = PI_viseur/np.linalg.norm(PI_viseur)
	# Computes hwo many times PI_viseur to reach board
	vec_dist = (-364.20-pos1[0])/PI_viseur[0]
	dy =  (pos1[1]+vec_dist*PI_viseur[1])-pos3[1]
	dz =  (pos1[2]+vec_dist*PI_viseur[2])-pos3[2]
	return dy,dz


	

if __name__ == '__main__':
	subject_id = get_subject()
	while 1 :
		PI_id = get_PI(subject_id)
		print('______\nReading results for : {0} and {1}\n______'.format(subject_id,PI_id))
		display_results_PI(subject_id,PI_id)
		plt.show()
	#~ display_results(subject_id)
	#~ print('\continue drawing ? ([y],n)')
	#~ ans  = raw_input()
	#~ if ans == 'n' :
		#~ plt.show()
		#~ sys.exit()
	#~ else : continue_drawing = 1
	#~ while continue_drawing == 1 :
		#~ subject_id = get_subject()
		#~ print('______\nReading results for : {0}\n______'.format(subject_id))
		#~ display_results(subject_id)
		#~ print('\continue drawing ? ([y],n)')
		#~ ans  = raw_input()
		#~ if ans == 'n' :
			#~ plt.show()
			#~ sys.exit()
		#~ else : continue_drawing = 1
	
	
		
	
