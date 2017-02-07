#!/usr/bin/env python

import rospy
import sys
import os
import message_filters
from IPython import embed
import matplotlib.pyplot as plt
import numpy as np
from mocap_align import mocap_extract, mocap_align_abs

global balls_centersy
global balls_centersx
global mes_bplume
global mes_brouge
global mes_bvide
mes_bplume = np.array([-3.6004087458,3.3680321189,1.5372971483])
mes_brouge = np.array([-3.6178109599,3.9675009516,1.5314543185])
mes_bvide = np.array([-3.6363492807,4.5560661391,1.5339595827])
balls_centersy = [3.3680321189,3.9675009516,4.5560661391]
balls_centersz = [1.5372971483,1.5314543185,1.5339595827]

def get_subject() :
	print('______\n\nsujet :')
	subject_id = raw_input()
	directory = '~/expego/data/'+subject_id+'/'
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
	directory = '~/expego/data/'+subject_id+'/'
	directory = os.path.expanduser(directory)
	while PI_id not in os.listdir(directory):
		print('entrer partie du corps\n')
		PI_id = raw_input();
	return PI_id

def get_session_nb() :
	print('______\n\nSession number :')
	session_nb = raw_input();
	return session_nb

def display_results(subject_id) :
	
	#~ balls_centersy = [5.0994-2.44/2,5.0994-2.44/2+0.61,5.0994-2.44/2-0.61]
	#~ balls_centersz = [2.1465-1.22/2,2.1465-1.22/2,2.1465-1.22/2]
	plt.plot(balls_centersy[0],balls_centersz[0],'go',markersize=40)
	plt.plot(balls_centersy[1],balls_centersz[1],'ro',markersize=40)
	plt.plot(balls_centersy[2],balls_centersz[2],'ko',markersize=40)
	plt.axis([2,6,0,3])
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

def display_results_PI (subject_id,PI_id,session_nb) :
	directory = '~/expego/data/'+subject_id
	directory = os.path.expanduser(directory)
	if not ('results.txt' in os.listdir(directory)):
		print('\nresults seems not to be already computed...\n______')
		return
	#~ balls_centersy = [5.0994-2.44/2,5.0994-2.44/2+0.61,5.0994-2.44/2-0.61]
	#~ balls_centersz = [2.1465-1.22/2,2.1465-1.22/2,2.1465-1.22/2]
	plt.plot(balls_centersy[0],balls_centersz[0],'go',markersize=40)
	plt.plot(balls_centersy[1],balls_centersz[1],'ro',markersize=40)
	plt.plot(balls_centersy[2],balls_centersz[2],'ko',markersize=40)
	plt.axis([0,6,0,5])		
	for balltype in os.listdir(directory+'/'+PI_id) :		
		balltypeminuscule = balltype.lower()
		if balltypeminuscule == 'red' :
			ballnb = 1
			colorflag = 'rx'
		elif balltypeminuscule == 'empty' :
			ballnb = 2
			colorflag = 'kx'
		elif balltypeminuscule == 'feather' :
			ballnb = 0
			colorflag = 'gx'
		for sessionname in session_nb :
			result_id = PI_id+','+balltype+','+sessionname
			print(result_id)
			with open(directory+'/results.txt','r') as results :
				for line in results :
					if result_id in  line :
						resultline = line.rsplit(',')
						resultline[-1] = resultline[-1].strip()
						ang = float(resultline[-1])
						print('Angle erreur : {0}'.format(ang))
						body_PI = mocap_extract(directory+'/'+PI_id+'/'+balltype+'/'+sessionname+'/'+'PI'+'.csv')
						body_viseur = mocap_extract(directory+'/'+PI_id+'/'+balltype+'/'+sessionname+'/'+'viseur'+'.csv')
						#~ embed()
						dy,dz = mocap_intercept(body_PI,body_viseur,balltype)
						print('Deviation Y : {0}\nDeviation Z : {1}'.format(dy,dz))
						plt.plot(balls_centersy[ballnb]+dy,balls_centersz[ballnb]+dz,colorflag,markersize=35)
						if not os.path.exists('results/'+subject_id):
							os.makedirs('results/'+subject_id)
						plt.savefig('results/'+subject_id+'/'+PI_id+'.pdf')
def save_results(subject_id) :
	
	directory = '~/expego/data/'+subject_id
	directory = os.path.expanduser(directory)
	if not ('results.txt' in os.listdir(directory)):
		print('\nresults seems not to be already computed...\n______')
		return

	for PI_id in os.listdir(directory) :
		if os.path.isdir(directory+'/'+PI_id) :
			#~ balls_centersy = [5.0994-2.44/2,5.0994-2.44/2+0.61,5.0994-2.44/2-0.61]
			#~ balls_centersz = [2.1465-1.22/2,2.1465-1.22/2,2.1465-1.22/2]
			plt.plot(balls_centersy[0],balls_centersz[0],'go',markersize=40)
			plt.plot(balls_centersy[1],balls_centersz[1],'ro',markersize=40)
			plt.plot(balls_centersy[2],balls_centersz[2],'ko',markersize=40)
			plt.axis([2,6,0,3])		
			for balltype in os.listdir(directory+'/'+PI_id) :		
				balltypeminuscule = balltype.lower()
				if balltypeminuscule == 'red' :
					ballnb = 1
					colorflag = 'rx'
				elif balltypeminuscule == 'empty' :
					ballnb = 2
					colorflag = 'kx'
				elif balltypeminuscule == 'feather' :
					ballnb = 0
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
								body_PI = mocap_extract(directory+'/'+PI_id+'/'+balltype+'/'+sessionname+'/'+'PI'+'.csv')
								body_viseur = mocap_extract(directory+'/'+PI_id+'/'+balltype+'/'+sessionname+'/'+'viseur'+'.csv')
								#~ embed()
								dy,dz = mocap_intercept(body_PI,body_viseur,balltype)
								print('Deviation Y : {0}\nDeviation Z : {1}'.format(dy,dz))
								plt.plot(balls_centersy[ballnb]+dy,balls_centersz[ballnb]+dz,colorflag,markersize=35)
								if not os.path.exists('results/'+subject_id):
									os.makedirs('results/'+subject_id)
								plt.savefig('results/'+subject_id+'/'+PI_id+'.pdf')
		plt.show()
	
def mocap_intercept(body_PI,body_viseur,ball) :
	# Computes positions of viseur and PI in cm
	pos_PI = np.array([np.mean(body_PI[:,0]),np.mean(body_PI[:,1]),np.mean(body_PI[:,2])])
	pos_viseur = np.array([np.mean(body_viseur[:,0]),np.mean(body_viseur[:,1]),np.mean(body_viseur[:,2])])

	# pos3 for balls board in second room
	#~ pos3 = np.array([-3.6420,5.0994-2.44/2,2.1465-1.22/2])*100
	
	# Offsets
	#~ pos1 = pos1 - np.array([0.0447,0,1.3750]) # PI offset
	#~ pos2 = pos2 - np.array([0.75,0,1.5]) # Viseur offset
	
	# Computes position of the three balls
	posred = mes_brouge
	posempty = mes_bvide
	posfeather = mes_bplume
	if ball.lower() == 'red' :
		pos3 = posred
	elif ball.lower() == 'feather' :
		pos3 = posfeather
	elif ball.lower() == 'empty' :
		pos3 = posempty
	else :
		return
			
	# Computes the interception
	PI_viseur = pos_viseur-pos_PI
	PI_viseur = PI_viseur/np.linalg.norm(PI_viseur)
	# Computes hwo many times PI_viseur to reach board
	vec_dist = (-3.617-pos_PI[0])/PI_viseur[0]
	dy =  (pos_PI[1]+vec_dist*PI_viseur[1])-pos3[1]
	dz =  (pos_PI[2]+vec_dist*PI_viseur[2])-pos3[2]

	return dy,dz

def main(argv) :
	subject_id = get_subject()
	#~ save_results(subject_id)
	while 1 :
		PI_id = get_PI(subject_id)
		session_nb = get_session_nb();
		print('______\nReading results for : {0} and {1}\n______'.format(subject_id,PI_id))
		display_results_PI(subject_id,PI_id,session_nb)
		plt.show()
	display_results(subject_id)
	print('\continue drawing ? ([y],n)')
	ans  = raw_input()
	if ans == 'n' :
		plt.show()
		sys.exit()
	else : continue_drawing = 1
	while continue_drawing == 1 :
		subject_id = get_subject()
		print('______\nReading results for : {0}\n______'.format(subject_id))
		display_results(subject_id)
		print('\continue drawing ? ([y],n)')
		ans  = raw_input()
		if ans == 'n' :
			plt.show()
			sys.exit()
		else : continue_drawing = 1

if __name__ == '__main__':
	main(sys.argv)

	
		
	
