import rclpy
import math
import time
from rclpy.node import Node
from rclpy.action import ActionServer
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from summer_task_interfaces.action import ExecuteCircle 
# 1. Import Multi-threading tools
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

class CirclePatrolServer(Node):
    def __init__(self):
        super().__init__('circle_patrol_server')
        
        # 2. Create a callback group that allows multiple functions to run at once
        self.cb_group = ReentrantCallbackGroup()
        
        self._action_server = ActionServer(
            self,
            ExecuteCircle,
            'execute_circle',
            self.execute_callback,
            callback_group=self.cb_group) # Assign to group
        
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        self.subscription = self.create_subscription(
            Pose, 
            '/turtle1/pose', 
            self.pose_callback, 
            10,
            callback_group=self.cb_group) # Assign to group
        
        self.current_pose = None
        self.safety_threshold = 1.5

    def pose_callback(self, msg):
        self.current_pose = msg

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing circular patrol...')
        
        while self.current_pose is None:
            time.sleep(0.1)

        radius = goal_handle.request.radius
        linear_v = 1.5
        angular_w = linear_v / radius
        
        start_x = self.current_pose.x
        start_y = self.current_pose.y
        
        feedback_msg = ExecuteCircle.Feedback()
        cmd = Twist()
        cmd.linear.x = linear_v
        cmd.angular.z = angular_w
        
        distance_traveled = 0.0
        start_time = time.time()
        
        while rclpy.ok():
            current_x = self.current_pose.x
            current_y = self.current_pose.y
            
            # The Wall-Crash Failure State
            if (current_x < self.safety_threshold) or (current_x > 11.0 - self.safety_threshold) or \
               (current_y < self.safety_threshold) or (current_y > 11.0 - self.safety_threshold):
                
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
                self.publisher_.publish(cmd)
                
                goal_handle.abort()
                result = ExecuteCircle.Result()
                result.success = False
                result.final_report = "Mission Aborted: Boundary Collision Imminent!"
                return result

            self.publisher_.publish(cmd)
            
            elapsed_time = time.time() - start_time
            distance_traveled = linear_v * elapsed_time
            feedback_msg.distance_traveled = distance_traveled
            feedback_msg.current_status = "Patrolling..."
            goal_handle.publish_feedback(feedback_msg)
            
            distance_to_start = math.sqrt((current_x - start_x)**2 + (current_y - start_y)**2)
            min_travel_distance = math.pi * radius 
            
            if distance_traveled > min_travel_distance and distance_to_start < 0.2:
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
                self.publisher_.publish(cmd)
                
                goal_handle.succeed()
                result = ExecuteCircle.Result()
                result.success = True
                result.final_report = "Mission Accomplished: Full loop completed safely."
                return result
            
            time.sleep(0.1)

def main(args=None):
    rclpy.init(args=args)
    server = CirclePatrolServer()
    # 3. Spin the node using the MultiThreadedExecutor
    executor = MultiThreadedExecutor()
    rclpy.spin(server, executor=executor)
    rclpy.shutdown()

if __name__ == '__main__':
    main()