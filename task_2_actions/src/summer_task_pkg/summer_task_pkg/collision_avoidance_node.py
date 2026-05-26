import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

class CollisionAvoidanceNode(Node):
    def __init__(self):
        super().__init__('collision_avoidance_node')
        
        self.declare_parameter('safety_threshold', 1.5)
        self.threshold = self.get_parameter('safety_threshold').get_parameter_value().double_value
        self.get_logger().info(f'Node started with safety_threshold: {self.threshold}')

        # Set up a timer to continuously check for parameter updates
        self.timer = self.create_timer(1.0, self.update_parameters)

    def update_parameters(self):
        # This fulfills the requirement to change the threshold at any time
        self.threshold = self.get_parameter('safety_threshold').get_parameter_value().double_value

    # Defining Explicit QoS Profile (Sensor Data)
        sensor_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=QoSReliabilityPolicy.BEST_EFFORT
        )

        # Creating Subscriber and Publisher
        self.pose_subscriber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            sensor_qos  # Applying the specific QoS here
        )
        
        self.velocity_publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10 # Standard QoS for publishing commands
        )
        
        self.cmd = Twist() 

    def pose_callback(self, msg):
        # Grid boundaries are 0.0 to 11.0
        x = msg.x
        y = msg.y
        
        # Check if we are within the safety threshold of any of the 4 walls
        if (x < self.threshold) or (x > 11.0 - self.threshold) or \
           (y < self.threshold) or (y > 11.0 - self.threshold):
            
            # Danger Zone: Override normal motion and spin
            self.get_logger().warn(f'Wall approaching! Distance threshold breached. Spinning...')
            self.cmd.linear.x = 0.0
            self.cmd.angular.z = 2.0  # Spin fast away from the wall
        else:
            # Safe Zone: Move forward
            self.cmd.linear.x = 1.0
            self.cmd.angular.z = 0.0
            
        self.velocity_publisher.publish(self.cmd)

def main(args=None):
    rclpy.init(args=args)
    node = CollisionAvoidanceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()