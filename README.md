# Summer Task 1: ROS 2 Workspace & Nodes

## Overview
This repository contains my first ROS 2 workspace, created for Summer Task 1. It includes two packages (`my_cpp_pkg` and `my_python_pkg`) that demonstrate basic Publisher/Subscriber communication broadcasting Ares-Nova telemetry.

## Packages
* **my_cpp_pkg**: A C++ package containing `cpp_pub` and `cpp_sub` nodes.
* **my_python_pkg**: A Python package containing `py_pub` and `py_sub` nodes.

## What I Learned
* How to initialize a ROS 2 workspace and configure version control (`.gitignore`).
* Creating C++ and Python packages using `ros2 pkg create`.
* Writing object-oriented Publisher and Subscriber nodes.
* Modifying `CMakeLists.txt` and `setup.py` to ensure executables are compiled and discoverable.
* Using `colcon build` and sourcing the workspace environment.
* Utilizing ROS 2 CLI tools to debug and visualize node networks.

## EXTRA TASK
### Topics vs Services
Topics (Publisher/Subscriber): Used for continuous, one-way data streams where the publisher simply broadcasts information without worrying about who is listening. In this workspace, I used Topics to constantly stream the Ares-Nova rover's telemetry pings.

Services (Client/Service): Used for synchronous, two-way "call-and-response" interactions. A client sends a specific request and waits for a reply before moving on. I implemented a Service to securely toggle the rover's autonomous driving mode, ensuring the system confirmed the mode change.

# Summer Task 2: ROS 2 Autonomous Navigation & Obstacle Avoidance

This repository contains the implementation of a custom ROS 2 (Humble) navigation stack utilizing Turtlesim. It demonstrates foundational autonomous behavior, including real-time sensor data processing, dynamic parameter tuning, and precision navigation using custom Action Servers and Multi-Threaded Executors.

## Prt 1: Project Structure

The workspace is divided into two primary packages:
* **`summer_task_interfaces`**: A CMake package containing the custom Action definitions (`ExecuteCircle.action`).
* **`summer_task_pkg`**: A Python package containing the core logic nodes, executors, and launch files.

## Key Features

### 1. Auto-Avoidance Telemetry (`collision_avoidance_node`)
A subscriber/publisher node that acts as a real-time safety override.
* **Explicit QoS:** Utilizes `Sensor Data` QoS (`BEST_EFFORT`, depth of 1) for the `/turtle1/pose` subscription to ensure the robot reacts to the absolute latest telemetry rather than delayed network queues.
* **Dynamic Parameters:** Implements a `safety_threshold` parameter (default: 1.5m) that can be dynamically tuned via the CLI at runtime without restarting the node—crucial for live-calibrating a mechanical chassis in the field.
* **Safety Override:** Continuously monitors the 11.0 x 11.0 grid boundaries. If breached, it overrides normal forward velocity and publishes an angular spin command to avoid a collision.

### 2. Precision Circular Patrol (`circle_patrol_server` & `circle_patrol_client`)
A custom Action Server/Client architecture for long-running, preemptable navigation tasks.
* **Dynamic Kinematics:** Calculates angular velocity on the fly based on the client's requested radius target (`w = v / radius`).
* **Multi-Threaded Execution:** Utilizes a `MultiThreadedExecutor` and `ReentrantCallbackGroup` to process continuous `/turtle1/pose` telemetry *while* executing the heavy while-loop of the Action goal, preventing node blindness.
* **Abortion Management:** If the requested patrol radius forces the robot into the boundary danger zone, the Action Server immediately halts the motors, sets the action state to `ABORTED`, and returns a failure report to the client.

---

## Build Instructions

Ensure you have ROS 2 Humble installed. Clone this repository into your `ros2_ws/src` directory and build both packages.

bash
# 1. Navigate to your workspace
cd ~/task_2_actions

# 2. Build the interfaces first
colcon build --packages-select summer_task_interfaces

# 3. Source the workspace
source install/setup.bash

# 4. Build the main Python package
colcon build --packages-select summer_task_pkg

# 5. Source again
source install/setup.bash

## Usage and Launch

Running Subtask A: Obstacle Avoidance Launch

This launch file starts the simulator and the custom collision avoidance node, passing a custom safety threshold of 2.0 meters.

bash
ros2 launch summer_task_pkg avoidance_launch.py

To test dynamic parameters in a new terminal: ros2 param set /collision_avoidance safety_threshold 3.0
Running Subtask B: Action Server Patrol

To execute the precision circular patrol, you will need three separate terminals (remember to source install/setup.bash in each).

Terminal 1 (Simulator):
bash
ros2 run turtlesim turtlesim_node

Terminal 2 (Action Server):
bash
ros2 run summer_task_pkg circle_patrol_server

Terminal 3 (Action Client):
bash
ros2 run summer_task_pkg circle_patrol_client

The client will request a 3.0m radius goal, print live distance tracking feedback, and report success upon completing a full 360-degree loop.

## Architectural Notes: The Communication Layer

This project was built to leverage the decentralized architecture of ROS 2.

* Unlike ROS 1, which relied on a single point of failure (the roscore Master), this system uses the Data Distribution Service (DDS) wire protocol.

* Nodes discover each other dynamically over the local network using the Simple Discovery Protocol (SDP) and multicast UDP.

* The underlying middleware can be swapped on the fly (e.g., eProsima Fast DDS, Eclipse Cyclone DDS) by configuring the RMW_IMPLEMENTATION environment variable.

## Part 2: Deep Dive into the Communication Layer

This project leverages the decentralized architecture of ROS 2. Understanding the underlying middleware is critical when designing robust autonomous systems (like an AutoNav suite) that cannot afford network blindspots.

### A. ROS 1 vs ROS 2 Architectural Shift

* **The Single Point of Failure (SPOF):** In ROS 1, every node relied on a centralized Master node (`roscore`) to negotiate connections. If the Master crashed, the entire system went blind—no new nodes could connect, and existing nodes could not discover new topics. 
* **Decentralized Architecture:** ROS 2 eliminates this SPOF entirely. It utilizes a fully peer-to-peer, decentralized architecture where nodes are autonomous and self-sufficient. If one sensor node crashes, the rest of the robotic network continues to operate seamlessly.
* **Network Protocol Upgrade:** ROS 1 relied on custom-built networking protocols (TCPROS/UDPROS). ROS 2 upgraded to the industry-standard **DDS (Data Distribution Service)** Wire Protocol, which is heavily utilized in aerospace and military applications for highly reliable, real-time data exchange.

### B. DDS (Data Distribution Service) & Middleware

* **The Discoverability Mechanism (SDP):** ROS 2 nodes discover each other on a local Wi-Fi network without a central server by using the **Simple Discovery Protocol (SDP)** backed by multicast UDP. When a node boots up, it broadcasts a multicast message declaring its existence. Other nodes actively listen to these multicast groups and dynamically establish direct, peer-to-peer connections.
* **Middleware Vendors:** Because ROS 2 abstracts the DDS layer, the network engine can be swapped on the fly based on mission requirements. Major integrated vendors include:
  * **eProsima Fast DDS** *(Default for ROS 2 Humble)*
  * **Eclipse Cyclone DDS**
  * **RTI Connext**
* **Switching Implementations:** The active DDS engine can be instantly changed without altering any source code by modifying the environment variable. For example: `export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`.