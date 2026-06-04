import sys
import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool

class RoverClient(Node):
    def __init__(self):
        super().__init__('rover_client_node')
        self.cli = self.create_client(SetBool, 'toggle_auto_mode')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
        self.req = SetBool.Request()

    def send_request(self, enable_auto):
        self.req.data = enable_auto
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

def main(args=None):
    rclpy.init(args=args)
    rover_client = RoverClient()
    
    # Grab the boolean argument from the command line
    enable_auto = sys.argv[1].lower() == 'true' if len(sys.argv) > 1 else True
    
    response = rover_client.send_request(enable_auto)
    rover_client.get_logger().info(f'Response: {response.message}')
    
    rover_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()