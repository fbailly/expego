#!/usr/bin/env python

import rospy
import sys
import os
import message_filters
from IPython import embed
from mocap_align import mocap_extract, mocap_align_abs

def get_subject() :
	print('______\n\nsujet :')
	subject_id = raw_input()
	return subject_id

def extract_data(subject_id) :
	directory = '~/catkin_ws/src/mocap/data/'+subject_id+'/'
	directory = os.path.expanduser(directory)
	if 'results.txt' in os.listdir(directory):
				print('\nresults already computed. Go ahead ? ([y],n)\n______')
				ans = raw_input()
				if ans == 'n' :
					return
	results = open(directory+'/results.txt','w')
	for filename in os.listdir(directory):
		PI_directory = directory+filename+'/'
		if os.path.isdir(PI_directory) :
			for ball_type in os.listdir(PI_directory) :
				ball_directory = PI_directory+ball_type+'/'
				for session in os.listdir(ball_directory) :
					session_directory = ball_directory+session+'/'
					print(filename)
					body1 = mocap_extract(session_directory+'/PI'+'.csv')
					body2 = mocap_extract(session_directory+'/viseur'+'.csv')
					ang = mocap_align_abs(body1,body2,ball_type)
					result_line = (filename+','+ball_type+','+session+','+str(ang)+'\n')
					results.write(result_line)
		else : break
	results.close


					
		

if __name__ == '__main__':
	subject_id = get_subject()
	print('______\n\nExtracting data for : {0}\n______'.format(subject_id))
	extract_data(subject_id)
	
