#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
import sys
import os
import message_filters
from optitrack.msg import or_pose_estimator_state
from std_msgs.msg import String
from IPython import embed
from mocap_align import mocap_extract, mocap_align_abs
from birappGUI import *

gui1 = GuiBirapp('gui1')
gui1.display_GUI('test',1)
subject_id = gui1.subject_id
f1 = open(gui1.os_directory+'PI'+'.csv', 'w')
f2 = open(gui1.os_directory+'viseur'+'.csv', 'w')
f1.writelines(gui1.l1tmp)
f2.writelines(gui1.l2tmp)
f1.close()
f2.close()
