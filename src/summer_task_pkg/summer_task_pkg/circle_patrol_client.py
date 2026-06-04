import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from summer_task_interfaces.action import ExecuteCircle 

class CirclePatrolClient(Node):
    def __init__(self):
        super().__init__('circle_patrol_client')
        self._action_client = ActionClient(self, ExecuteCircle, 'execute_circle')

    def send_goal(self, radius):
        goal_msg = ExecuteCircle.Goal()
        goal_msg.radius = radius

        self.get_logger().info(f'Waiting for action server to start...')
        self._action_client.wait_for_server()

        self.get_logger().info(f'Sending goal request: Radius = {radius}m')
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, 
            feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted, executing circle patrol...')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'[{feedback.current_status}] Distance traveled: {feedback.distance_traveled:.2f} meters')

    def get_result_callback(self, future):
        result = future.result().result
        
        if result.success:
            self.get_logger().info(f'SUCCESS! {result.final_report}')
        else:
            self.get_logger().error(f'FAILED! {result.final_report}')
            
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    action_client = CirclePatrolClient()
    action_client.send_goal(3.0) 
    rclpy.spin(action_client)

if __name__ == '__main__':
    main()
