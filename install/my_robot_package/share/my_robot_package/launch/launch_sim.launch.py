import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():

    # 1. FIND YOUR FILES
    # (Replace 'my_robot_package' with the actual name of your ROS folder)
    pkg_path = os.path.join(get_package_share_directory('my_robot_package'))
    xacro_file = os.path.join(pkg_path, 'description', 'robot.urdf.xacro')
    world_file = os.path.join(pkg_path, 'worlds', 'world.sdf')
    
    # Process the Xacro file into a computer-readable string
    robot_description_config = xacro.process_file(xacro_file)
    robot_desc = {'robot_description': robot_description_config.toxml()}

    # ==============================================
    # 2. THE REQUIRED PUBLISHERS 
    # ==============================================
    
    # Robot State Publisher 
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_desc]
    )

    # Joint State Publisher 
    node_joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen'
    )

    # ==============================================
    # 3. START THE SIMULATOR & SPAWN ROBOT
    # ==============================================

    # Start Gazebo Ignition and load your SDF world file
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_ign_gazebo'), 'launch', 'ign_gazebo.launch.py')]),
        launch_arguments={'ign_args': world_file}.items()
    )

    # Spawn the robot into the Gazebo world using the blueprint
    spawn_entity = Node(
        package='ros_ign_gazebo',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_rover'],
        output='screen'
    )

    # ==============================================
    # 4. ACTION! (Run everything at once)
    # ==============================================
    return LaunchDescription([
        node_robot_state_publisher,
        node_joint_state_publisher,
        gazebo,
        spawn_entity
    ])