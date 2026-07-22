#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import os
from math import cos, sin, sqrt, atan2, pi
from geometry_msgs.msg import Point
from nav_msgs.msg import Odometry, Path
from morai_msgs.msg import CtrlCmd
from tf.transformations import euler_from_quaternion


class pure_pursuit:
    def __init__(self):
        rospy.init_node('pure_pursuit', anonymous=True)

        # Subscribe
        rospy.Subscriber('/local_path', Path, self.path_callback)
        rospy.Subscriber('/odom', Odometry, self.odom_callback)

        # Publish
        self.ctrl_cmd_pub = rospy.Publisher('/ctrl_cmd_0', CtrlCmd, queue_size=1)
        self.ctrl_cmd_msg = CtrlCmd()
        self.ctrl_cmd_msg.longlCmdType = 2   # velocity control mode

        self.is_path = False
        self.is_odom = False

        self.path = Path()
        self.current_position = Point()
        self.vehicle_yaw = 0.0

        # MORAI 차량 파라미터
        self.vehicle_length = 1.0   # wheel base [m]
        self.lfd = 3.5              # look forward distance [m]
        # 과제 주행 속도
        self.target_velocity = 15.0

        rate = rospy.Rate(15)

        while not rospy.is_shutdown():

            if self.is_path and self.is_odom:
                steering, is_forward_point = self.calc_pure_pursuit()

                if is_forward_point:
                    self.ctrl_cmd_msg.steering = steering
                    self.prev_steering = steering
                    self.ctrl_cmd_msg.velocity = self.get_velocity_by_steering(steering)
                    self.ctrl_cmd_msg.accel = 0.0
                    self.ctrl_cmd_msg.brake = 0.0
                else:
                    self.ctrl_cmd_msg.steering = self.prev_steering
                    self.ctrl_cmd_msg.velocity = 5.0
                    self.ctrl_cmd_msg.accel = 0.0
                    self.ctrl_cmd_msg.brake = 0.0
                    rospy.logwarn_throttle(1.0, "No forward point found")

                self.ctrl_cmd_pub.publish(self.ctrl_cmd_msg)

                os.system('clear')
                print("-------------------------------------")
                print("Pure Pursuit Control")
                print("steering [deg] :", self.ctrl_cmd_msg.steering * 180.0 / pi)
                print("velocity [kph] :", self.ctrl_cmd_msg.velocity)
                print("lfd [m]        :", self.lfd)
                print("-------------------------------------")

            else:
                os.system('clear')
                if not self.is_path:
                    print("[1] can't subscribe '/local_path' topic...")
                if not self.is_odom:
                    print("[2] can't subscribe '/odom' topic...")

            # self.is_path = False
            # self.is_odom = False
            rate.sleep()

    def calc_pure_pursuit(self):
        ego_x = self.current_position.x
        ego_y = self.current_position.y
        ego_yaw = self.vehicle_yaw

        selected_local_x = None
        selected_local_y = None
        max_front_dis = 0.0
        fallback_local_x = None
        fallback_local_y = None

        for pose in self.path.poses:
            path_x = pose.pose.position.x
            path_y = pose.pose.position.y

            dx = path_x - ego_x
            dy = path_y - ego_y

            local_x = cos(ego_yaw) * dx + sin(ego_yaw) * dy
            local_y = -sin(ego_yaw) * dx + cos(ego_yaw) * dy

            if local_x > 0.0:
                dis = sqrt(local_x ** 2 + local_y ** 2)

                # lfd 이상인 첫 번째 전방점
                if dis >= self.lfd:
                    selected_local_x = local_x
                    selected_local_y = local_y
                    break

                # lfd보다 짧아도 가장 먼 전방점을 fallback으로 저장
                if dis > max_front_dis:
                    max_front_dis = dis
                    fallback_local_x = local_x
                    fallback_local_y = local_y

        # lfd 이상 점이 없으면, 가장 먼 전방점을 사용
        if selected_local_x is None:
            if fallback_local_x is None:
                return 0.0, False

            selected_local_x = fallback_local_x
            selected_local_y = fallback_local_y

        theta = atan2(selected_local_y, selected_local_x)
        # lookahead = max(sqrt(selected_local_x ** 2 + selected_local_y ** 2), 1.0)

        steering = atan2(
            2.0 * self.vehicle_length * sin(theta),
            self.lfd
        )

        steering = max(min(steering, 0.7), -0.7)

        return steering, True

    def get_velocity_by_steering(self, steering):
        abs_steering = abs(steering)

        # 코너에서는 감속
        if abs_steering > 0.35:
            return 8.0
        elif abs_steering > 0.20:
            return 12.0
        else:
            return self.target_velocity

    def path_callback(self, msg):
        self.is_path = True
        self.path = msg

    def odom_callback(self, msg):
        self.is_odom = True

        odom_quaternion = (
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w
        )

        _, _, self.vehicle_yaw = euler_from_quaternion(odom_quaternion)

        self.current_position.x = msg.pose.pose.position.x
        self.current_position.y = msg.pose.pose.position.y


if __name__ == '__main__':
    try:
        test_track = pure_pursuit()
    except rospy.ROSInterruptException:
        pass