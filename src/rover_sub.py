import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class RoverSubscriber(Node):
    def __init__(self):
        super().__init__('py_rover_subscriber')
        self.subscription = self.create_subscription(
            String,
            'ares_nova_telemetry',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'Received Data: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    rover_subscriber = RoverSubscriber()
    rclpy.spin(rover_subscriber)
    rover_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()