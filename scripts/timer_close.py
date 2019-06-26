#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
from rosgraph_msgs.msg import Clock
import time

class Timer():

    def __init__(self):
        self.cmd_vel_subscriber = rospy.Subscriber('/cmd_vel', Twist, self.sub_callback)
        self.cmd_vel_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.clock_sub = rospy.Subscriber('/clock', Clock , self.sub_clock)
        self.ctrl_c = False
        self.ref_time = -1
        self.current_time = -1
        rospy.on_shutdown(self.shutdownhook)
        self.rate = rospy.Rate(1)

    def init_timer(self):
        self.ref_time = self.current_time

    def sub_clock(self, msg):
        self.current_time = msg.clock.secs
        if self.ref_time == -1:
            self.init_timer()
        print 'Seconds without cmd_vel cmd:' + str((self.current_time - self.ref_time))
        if (self.current_time - self.ref_time) > 0.5:
            self.stop_robot()
            self.init_timer()

        print 'Ref Time:' + str(self.ref_time)
        print 'Current Time:' + str(self.current_time)


    def sub_callback(self, msg):
        self.init_timer()

    def publish_once_in_cmd_vel(self, cmd):
        while not self.ctrl_c:
            connections = self.cmd_vel_publisher.get_num_connections()
            if connections > 0:
                self.cmd_vel_publisher.publish(cmd)
                break
            else:
                self.rate.sleep()

    def shutdownhook(self):
        self.stop_robot()
        self.ctrl_c = True

    def stop_robot(self):
        cmd = Twist()
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0
        self.publish_once_in_cmd_vel(cmd)

if __name__ == '__main__':
    rospy.init_node('timer_test', anonymous=True)
    timer_object = Timer()
    rospy.spin()