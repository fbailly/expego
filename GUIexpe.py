#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import sys
import os
import message_filters
from optitrack.msg import or_pose_estimator_state
from std_msgs.msg import String
from IPython import embed
from GuiMocap import GuiMocap
from mocap_align import mocap_extract, mocap_align_abs
	
def main(argv) :
	subject_id = argv[1]
	#~ session_id = argv[2]
	gui1 = GuiMocap('gui1')
	gui1.display_GUI(subject_id)
	subject_id = gui1.subject_id
	f1 = open(gui1.os_directory+'PI'+'.csv', 'w')
	f2 = open(gui1.os_directory+'viseur'+'.csv', 'w')
	f1.writelines(gui1.l1tmp)
	f2.writelines(gui1.l2tmp)
	f1.close()
	f2.close()
	body1 = mocap_extract(gui1.os_directory+'PI'+'.csv')
	body2 = mocap_extract(gui1.os_directory+'viseur'+'.csv')
	ang = mocap_align_abs(body1,body2,gui1.target_id)
	print('______\n\nAngle erreur : {0}\n______\n'.format(ang))

if __name__ == '__main__' :
	main(sys.argv)
