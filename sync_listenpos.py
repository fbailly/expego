#!/usr/bin/env python

import rospy
import sys
import os
import message_filters
from optitrack.msg import or_pose_estimator_state
from std_msgs.msg import String
from IPython import embed
from mocap_align import mocap_extract, mocap_align_abs
counter = 0
sync = True
l1 = []
l1tmp = []
l2 = []
l2tmp = []
l3 = []
l3tmp = []
coord = ['x','y','z','qw','qx','qy','qz']
def callback(data1,data2):
	global sync
	global l1
	global l2
	global l3
	global counter 
	global coord
	global duration1
	global duration2
	global duration3
	ts1 = data1.ts # timestamps
	ts2 = data2.ts
	#~ ts3 = data3.ts
	pos1 = data1.pos # positions
	pos2 = data2.pos
	#~ pos3 = data3.pos
	tmpsync = (ts1==ts2) # synchro flag
	sync = tmpsync and sync

	for i in range(7) :
		l1.append(str(str(eval('pos1[0].'+coord[i])) + ','))
		l2.append(str(str(eval('pos2[0].'+coord[i])) + ','))
		#~ l3.append(str(str(eval('pos3[0].'+coord[i])) + ','))
		if i==6 :
			l1.append(str('\n'))
			l2.append(str('\n'))
			#~ l3.append(str('\n'))
			
	counter +=1
	if counter == 1 :
		duration1 = ts1
		duration2 = ts2
		#~ duration3 = ts3
	if counter>50 :
		print('\nFrames : '+ str(counter))
		print('Synchro : ' + str(sync) )
		duration1 = ts1.sec-duration1.sec + pow(10,-9)*(ts1.sec-duration1.nsec)
		duration2 = ts2.sec-duration2.sec + pow(10,-9)*(ts2.sec-duration2.nsec)
		#~ duration3 = ts3.sec-duration3.sec + pow(10,-9)*(ts3.sec-duration3.nsec)
		# gather lists
		l1tmp.append('Frames : ' + str(counter) + '\n')
		l1tmp.append('Synchro : ' + str(sync) + '\n' )
		l1tmp.append('Duration : ' + str(duration1) + '\n' )
		l2tmp.append('Frames : ' + str(counter) + '\n')
		l2tmp.append('Synchro : ' + str(sync) + '\n')
		l2tmp.append('Duration : ' + str(duration2) + '\n' )
		#~ l3tmp.append('Frames : ' + str(counter) + '\n')
		#~ l3tmp.append('Synchro : ' + str(sync) + '\n')
		#~ l3tmp.append('Duration : ' + str(duration3) + '\n' )
		l1tmp.extend(l1)
		l2tmp.extend(l2)
		#~ l3tmp.extend(l3)
		# write to file
		f1.writelines(l1tmp)
		f2.writelines(l2tmp)
		#~ f3.writelines(l3tmp)
		rospy.signal_shutdown(listener)

def listener():

    rospy.init_node('listener', anonymous=True)
    chat1_sub = message_filters.Subscriber('/optitrack/bodies/'+'PI', or_pose_estimator_state)
    chat2_sub = message_filters.Subscriber('/optitrack/bodies/'+'viseur', or_pose_estimator_state)
    #~ chat3_sub = message_filters.Subscriber('/optitrack/bodies/'+'target', or_pose_estimator_state)
    ts = message_filters.ApproximateTimeSynchronizer([chat1_sub, chat2_sub], 51,1, allow_headerless=True)
    ts.registerCallback(callback)
    rospy.spin()

def get_info() :
	print('______\n\nentrer code sujet :')
	subject_id = raw_input()
	print('______\n\nentrer code emplacement PI :')
	PI_id = raw_input()
	print('______\n\nentrer code cible :')
	target_id = raw_input()
	print('______\n\nentrer numero de session :')
	session_nb = raw_input()
	return subject_id,PI_id,session_nb,target_id
	

if __name__ == '__main__':
	subject_id,PI_id,session_nb,target_id = get_info()
	directory = '~/catkin_ws/src/mocap/data/'+subject_id+'/'+PI_id+'/'+target_id+'/'+session_nb+'/'
	os_directory = os.path.expanduser(directory)
	print('______\n\nPerforming motion capture for :\nSubject : {0}\nPI : {1}\nTarget : {2}\nSession : {3}\n______'.format(subject_id,PI_id,target_id,session_nb))
	print('\n'+os_directory+'\n')
	if os.path.exists(os_directory):
		print('session already created, erase it ? ([y], n)')
		ans = raw_input()
		if ans == 'n' :
			session_nb = str(max((list(map(int,os.listdir(os.path.expanduser('~/catkin_ws/src/mocap/data/'+subject_id+'/'+PI_id+'/'+target_id))))))+1)
			directory = '~/catkin_ws/src/mocap/data/'+subject_id+'/'+PI_id+'/'+target_id+'/'+session_nb+'/'
			os_directory = os.path.expanduser(directory)
	if not os.path.exists(os_directory):
		os.makedirs(os_directory)
	f1 = open(os_directory+'PI'+'.csv', 'w')
	f2 = open(os_directory+'viseur'+'.csv', 'w')
	listener()
	f1.close()
	f2.close()
	body1 = mocap_extract(os_directory+'PI'+'.csv')
	body2 = mocap_extract(os_directory+'viseur'+'.csv')
	ang = mocap_align_abs(body1,body2,target_id) 
	print('______\n\nAngle erreur : {0}\n______\n'.format(ang))

