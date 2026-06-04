from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Start the standard turtlesim node
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim'
        ),
        # Start your custom collision avoidance node
        Node(
            package='summer_task_pkg',
            executable='collision_avoidance_node',
            name='collision_avoidance',
            parameters=[
                {'safety_threshold': 2.0} # Custom launch-time value
            ]
        )
    ])