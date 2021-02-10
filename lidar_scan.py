#! /usr/bin/env python

import rospy, time
from sensor_msgs.msg import LaserScan
from xycar_motor.msg import xycar_motor

import signal
import sys
import os

def signal_handler(sig, frame):
	os.system('killall -9 python rosout')
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Variables
motor_msg = xycar_motor()
pub = None
lidar_range = []
limit = 0
limit_before = 0

def callback(data):
	global lidar_range, motor_msg
	lidar_range = data.ranges

def scan_lidar():
    global limit, limit_before, lidar_range
    limit_before = limit
    print('---',limit,'---',limit_before)
    for degree in range(44,134):	# scan degree
        if lidar_range[degree] <= 0.4:
            print(lidar_range[degree])
            limit += 1
    if limit > limit_before:
		return False
    return True

def drive(angle, delay):
    global motor_msg, pub
    for cnt in range(delay):
        motor_msg.speed = 3
        motor_msg.angle = angle
        pub.publish(motor_msg)
        rospy.sleep(0.1)

def stop_msg(delay):
	global motor_msg, pub
	for cnt in range(delay):
		motor_msg.speed = 0
		motor_msg.angle = 0
		pub.publish(motor_msg)
		rospy.sleep(0.1)

rospy.init_node('lidar_scan', anonymous = True)
rospy.Subscriber('/scan', LaserScan, callback, queue_size = 1)
pub = rospy.Publisher('xycar_motor', xycar_motor, queue_size = 1)

rospy.sleep(3)

print("---------- lidar scan drive start ----------")

while not rospy.is_shutdown():
	if scan_lidar():
		drive(0,10)
	else:
		drive(30,10)	# drive right for obstacles
		






