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
flag = 0
start = 0
end = 0

def callback(data):
	global lidar_range, motor_msg
	lidar_range = data.ranges

def avoid_obstacles():
    global limit, lidar_range, flag, start, end

    for degree in range(40, 190):       # left = 0', right = 180'
        # Obstacles in front of vehicle -> go left
        if flag == 0 and 44 < degree < 134 and lidar_range[degree] <= 0.75:
            flag = 1
            limit = 1
            print('Go Left')
            print(lidar_range[degree], degree)
            
        if flag == 1 and 175 < degree < 189 and 0.45 < lidar_range[degree] <= 0.8:
            flag = 2
            limit = 2
            print('Go Right')
            print(lidar_range[degree], degree)
        
        if flag == 2 and 185 < degree < 189 and 0.1 < lidar_range[degree] < 0.3:
            flag = 3
            limit = 3
            start = time.time()
            print(start)
            print('Go Straight')
            print(lidar_range[degree], degree)
        
        if flag == 3:
            end = time.time()
            if end - start >= 6:
                limit = 4

def drive(angle, speed):
    global motor_msg, pub
    motor_msg.speed = speed
    motor_msg.angle = angle
    pub.publish(motor_msg)

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
    avoid_obstacles()
    if limit == 0:
        drive(0, 3)
    if limit == 1:
        drive(-40, 2)
    if limit == 2:
        drive(50, 2)
    if limit == 3:
        drive(20, 2)
    if limit == 4:
        drive(-7, 2)






