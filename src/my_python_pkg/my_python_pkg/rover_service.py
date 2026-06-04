import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool

class RoverService(Node):
    def __init__(self):
        super().__init__('rover_service_node')
        self.srv = self.create_service(SetBool, 'toggle_auto_mode', self.toggle_callback)
        self.get_logger().info('Ares-Nova Mode Toggle Service is ready.')

    def toggle_callback(self, request, response):
        if request.data:
            response.success = True
            response.message = 'Autonomous mode ENGAGED.'
        else:
            response.success = True
            response.message = 'Autonomous mode DISENGAGED. Manual override active.'
        
        self.get_logger().info(f'Incoming request. Setting Auto Mode: {request.data}')
        return response

def main(args=None):
    rclpy.init(args=args)
    rover_service = RoverService()
    rclpy.spin(rover_service)
    rclpy.shutdown()

if __name__ == '__main__':
    main()