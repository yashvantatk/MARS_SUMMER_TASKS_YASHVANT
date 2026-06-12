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
        parameters=[robot_desc, {'use_sim_time': True}]
    )

    # ==============================================
    # 3. START THE SIMULATOR & SPAWN ROBOT
    # ==============================================

    # Start Gazebo Ignition and load your SDF world file
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_ign_gazebo'), 'launch', 'ign_gazebo.launch.py')]),
        launch_arguments={'ign_args': '-r ' + world_file}.items()
    )

    # Spawn the robot into the Gazebo world using the blueprint
    spawn_entity = Node(
        package='ros_ign_gazebo',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_rover'],
        output='screen'
    )
    
    # ==============================================
    # 4. THE DATA BRIDGE (Translating Gazebo -> ROS)
    # ==============================================
    
    # We are bridging three topics: The Lidar scan, the Camera image, and the IMU data.
    # The syntax is: /gazebo_topic@ROS_Message_Type@/ros_topic
    
    # We are bridging three topics plus the Simulation Clock
    bridge = Node(
        package='ros_ign_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan@ignition.msgs.LaserScan',
            '/camera/image_raw@sensor_msgs/msg/Image@ignition.msgs.Image',
            '/imu/data@sensor_msgs/msg/Imu@ignition.msgs.IMU',
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock'
        ],
        output='screen'
    )
    
    # Wakes up the state broadcaster
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    # Wakes up the arm motor
    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller"],
    )
    
    # ==============================================
    # 5. ACTION! (Run everything at once)
    # ==============================================
    return LaunchDescription([
        node_robot_state_publisher,
        gazebo,
        spawn_entity,
        bridge,
        joint_state_broadcaster_spawner,
        arm_controller_spawner
    ])
