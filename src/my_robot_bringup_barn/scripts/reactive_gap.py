#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from rclpy.qos import qos_profile_sensor_data
import numpy as np
import math

class ReactiveGapFollower(Node):
    def __init__(self):
        super().__init__('reactive_gap_follower')
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_cb, qos_profile_sensor_data)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.max_speed = 2.5
        self.max_turn = 3.5
        self.chassis_radius = 0.24 
        self.get_logger().info("Raw Kinematic Gap Follower Active.")

    def scan_cb(self, msg):
        ranges = np.array(msg.ranges)
        ranges = np.clip(ranges, 0.0, msg.range_max)
        
        angle_min = msg.angle_min
        angle_increment = msg.angle_increment
        
        # Slices out the forward 180-degree field of view
        start_idx = max(0, int((-1.57 - angle_min) / angle_increment))
        end_idx = min(len(ranges), int((1.57 - angle_min) / angle_increment))
        front_ranges = ranges[start_idx:end_idx]
        
        if len(front_ranges) == 0:
            return
            
        closest_idx = np.argmin(front_ranges)
        min_dist = front_ranges[closest_idx]
        
        # Immediate recovery spin if a wall gets inside the safety radius
        if min_dist < self.chassis_radius:
            self.send_cmd(0.0, self.max_turn if closest_idx < len(front_ranges)/2 else -self.max_turn)
            return

        # Zero out the indices inside the obstacle's physical footprint bubble
        bubble_size = int(math.atan2(self.chassis_radius, min_dist) / angle_increment)
        bubble_start = max(0, closest_idx - bubble_size)
        bubble_end = min(len(front_ranges), closest_idx + bubble_size)
        front_ranges[bubble_start:bubble_end] = 0.0
        
        # Locate valid clearances
        threshold = 1.1
        gaps = front_ranges > threshold
        
        if not np.any(gaps):
            self.send_cmd(-0.3, self.max_turn)
            return
            
        labeled_gaps = np.diff(np.concatenate(([0], gaps.astype(int), [0])))
        starts = np.where(labeled_gaps == 1)[0]
        ends = np.where(labeled_gaps == -1)[0]
        lengths = ends - starts
        largest_gap_idx = np.argmax(lengths)
        
        gap_start = starts[largest_gap_idx]
        gap_end = ends[largest_gap_idx]
        
        # Calculate target vector relative to absolute lidar coordinate frame
        target_idx_local = gap_start + (gap_end - gap_start) // 2
        target_idx_absolute = start_idx + target_idx_local
        target_angle = angle_min + (target_idx_absolute * angle_increment)
        
        # Scale speed dynamically relative to steering severity
        velocity = self.max_speed * (1.0 - abs(target_angle) / 1.57)
        steering = target_angle * 2.2 
        
        velocity = max(0.2, min(velocity, self.max_speed))
        steering = max(-self.max_turn, min(steering, self.max_turn))
        
        self.send_cmd(velocity, steering)

    def send_cmd(self, linear, angular):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.cmd_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ReactiveGapFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
