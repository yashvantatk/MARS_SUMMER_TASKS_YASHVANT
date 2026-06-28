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

---

## EXTRA TASK
### Topics vs Services
Topics (Publisher/Subscriber): Used for continuous, one-way data streams where the publisher simply broadcasts information without worrying about who is listening. In this workspace, I used Topics to constantly stream the Ares-Nova rover's telemetry pings.

Services (Client/Service): Used for synchronous, two-way "call-and-response" interactions. A client sends a specific request and waits for a reply before moving on. I implemented a Service to securely toggle the rover's autonomous driving mode, ensuring the system confirmed the mode change.

---

# Summer Task 2: ROS 2 Autonomous Navigation & Obstacle Avoidance

This repository contains the implementation of a custom ROS 2 (Humble) navigation stack utilizing Turtlesim. It demonstrates foundational autonomous behavior, including real-time sensor data processing, dynamic parameter tuning, and precision navigation using custom Action Servers and Multi-Threaded Executors.

## Part 1: Project Structure

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

## Build Instructions

Ensure you have ROS 2 Humble installed. Clone this repository into your `ros2_ws/src` directory and build both packages.

### 1. Navigate to your workspace
```bash
cd ~/task_2_actions
```

### 2. Build the interfaces first
```bash
colcon build --packages-select summer_task_interfaces
```

### 3. Source the workspace
```bash
source install/setup.bash
```

### 4. Build the main Python package
```bash
colcon build --packages-select summer_task_pkg
```

### 5. Source again
```bash
source install/setup.bash
```

## Usage and Launch

### Running Subtask A: Obstacle Avoidance Launch

This launch file starts the simulator and the custom collision avoidance node, passing a custom safety threshold of 2.0 meters.

```bash
ros2 launch summer_task_pkg avoidance_launch.py
```
To test dynamic parameters in a new terminal: ros2 param set /collision_avoidance safety_threshold 3.0

### Running Subtask B: Action Server Patrol

To execute the precision circular patrol, you will need three separate terminals (remember to source install/setup.bash in each).

Terminal 1 (Simulator):
```bash
ros2 run turtlesim turtlesim_node
```
Terminal 2 (Action Server):
```bash
ros2 run summer_task_pkg circle_patrol_server
```
Terminal 3 (Action Client):
```bash
ros2 run summer_task_pkg circle_patrol_client
```
The client will request a 3.0m radius goal, print live distance tracking feedback, and report success upon completing a full 360-degree loop.

## Architectural Notes: The Communication Layer

This project was built to leverage the decentralized architecture of ROS 2.

* Unlike ROS 1, which relied on a single point of failure (the roscore Master), this system uses the Data Distribution Service (DDS) wire protocol.

* Nodes discover each other dynamically over the local network using the Simple Discovery Protocol (SDP) and multicast UDP.

* The underlying middleware can be swapped on the fly (e.g., eProsima Fast DDS, Eclipse Cyclone DDS) by configuring the RMW_IMPLEMENTATION environment variable.

---

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

---

# SUMMER TASK 3 - ROBOT SIMULATION SETUP

## Task Overview
* **URDF/Xacro:** Designed a central chassis (blue box) with 4 continuous wheels (black cylinders) including visual, collision, and inertial properties.
* **Gazebo:** Created an SDF world with an infinite static ground plane, directional sunlight, and physics parameters.
* **Launch File:** Wrote a Python launch script (`launch_sim.launch.py`) to initialize `robot_state_publisher`, `joint_state_publisher`, Gazebo, and the entity spawner.
* **RVIZ2:** Visualized the generated RobotModel and the mathematical TF Tree.

## Package Structure
```text
my_robot_package/
├── CMakeLists.txt         # Configured to install launch, description, worlds, and rviz folders
├── package.xml
├── .gitignore             # Ignores ROS 2 build files (build/, install/, log/, __pycache__)
├── description/
│   └── robot.urdf.xacro   # The Ares-Nova robot blueprint (with dummy_root KDL fix)
├── launch/
│   └── launch_sim.launch.py # Master launch file
├── worlds/
│   └── world.sdf          # The Gazebo simulation environment
└── rviz/                  # (Optional) Saved RVIZ configuration files
```

## Dependencies & Installation commands

**1. Install Gazebo Ignition (Fortress):**
```bash
sudo sh -c 'echo "deb [http://packages.osrfoundation.org/gazebo/ubuntu-stable](http://packages.osrfoundation.org/gazebo/ubuntu-stable) `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list'
wget [http://packages.osrfoundation.org/gazebo.key](http://packages.osrfoundation.org/gazebo.key) -O - | sudo apt-key add -
sudo apt-get update
sudo apt-get install libignition-gazebo6-dev ignition-fortress
```

**2.Install Ros2 Packages & Bridges:**
```bash
# Xacro parser
sudo apt install ros-humble-xacro

# ROS-Ignition Bridge (allows ROS to talk to Gazebo)
sudo apt install ros-humble-ros-ign

# State Publishers (for TF Trees)
sudo apt install ros-humble-joint-state-publisher ros-humble-robot-state-publisher
```

## Workspace Setup & Build Commands

**1.Creating workspace and package:**
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake my_robot_package
cd my_robot_package
mkdir description worlds launch rviz
touch .gitignore
```

**2.Build and Source**
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake my_robot_package
cd my_robot_package
mkdir description worlds launch rviz
touch .gitignore
```

**3.Clean Build(in case of any error)**
```bash
cd ~/ros2_ws
rm -rf build install log
colcon build
source install/setup.bash
```

## Running the Simulation

**Step 1: Launch Gazebo**
```bash
cd ~/ros2_ws
source install/setup.bash
ros2 launch my_robot_package launch_sim.launch.py
```

**Step 2: Visualize TF Tree in RVIZ2**
```bash
cd ~/ros2_ws
source install/setup.bash
rviz2
```

**RVIZ Configuration Steps:**
1.Set Fixed Frame to dummy_root.
2.Click Add -> Select RobotModel.
3.Expand RobotModel -> Set Description Topic to /robot_description.
4.Click Add -> Select TF (adjust Marker Scale to 0.3 if arrows are too large).

## Development Notes

- CMakeLists.txt Trick: Always ensure the install(DIRECTORY ...) block is added at the bottom of the CMake file before ament_package(), otherwise ROS will not copy your folders into the build.

- The KDL Inertia Bug: If the wheels fail to spawn and terminal throws a "KDL does not support a root link with an inertia" error, a weightless <link name="dummy_root"/> attached via a fixed joint to the base_link must be added to the top of the URDF.

---

# Summer Task 4: ROS 2 & Gazebo Robot Simulation

## Overview
This package contains a fully functional URDF robot model (`my_rover`) simulated in Ignition Gazebo. The robot is equipped with a camera, Lidar, and IMU, and utilizes `ros2_control` to actuate a robotic arm via a remote control interface.

## Prerequisites
Ensure the necessary ROS 2 Humble control packages are installed:
```bash
sudo apt install ros-humble-ros2-control ros-humble-ros2-controllers ros-humble-ign-ros2-control ros-humble-rqt-joint-trajectory-controller
```

## Steps to run the simulation

**1.  Build Workspace**
```bash
cd ~/ros2_ws
colcon build --packages-select my_robot_package
source install/setup.bash
```

**2. Launch Gazebo and Rviz2**

Create a launch file. This single launch file spawns the robot in Gazebo, auto-starts the physics engine, bridges all sensor data, and wakes up the ros2_control nervous system:
```bash
ros2 launch my_robot_package launch_sim.launch.py
```

**3. Launch the remote ARM CONTROL**
To move the robotic arm, open a new terminal and launch the RQT controller.
Note: The --ros-args -p use_sim_time:=true flag is required to sync the controller's clock with Gazebo.
```bash
source ~/ros2_ws/install/setup.bash
ros2 run rqt_joint_trajectory_controller rqt_joint_trajectory_controller --ros-args -p use_sim_time:=true
```
---

# 🛰️ Task 5: Ares-Nova Autonomous Rover — Unified Visual Cortex Integration

> ROS 2 (Humble) packages and computer vision pipeline for the Ares-Nova rover, fusing a custom-trained YOLOv8 model with OpenCV ArUco pose estimation into a single perception node.

---

## 📑 Table of Contents

1. [Task Overview](#1-task-overview)
2. [Process Flow](#2-process-flow)
3. [File Structure & Contents](#3-file-structure--contents)
4. [Obstacles Faced & Engineering Solutions](#4-obstacles-faced--engineering-solutions)
5. [Key Things Learned](#5-key-things-learned)
6. [Essential Bash Commands (Cheat Sheet)](#6-essential-bash-commands-cheat-sheet)

---

## 1. Task Overview

This repository contains the ROS 2 (Humble) packages and computer vision scripts for the **Ares-Nova rover**. The core objective of this phase was to build a **"Unified Visual Cortex"** — a single ROS 2 node capable of:

- Running a **custom-trained YOLOv8** neural network to detect specific traffic cones, **and**
- Simultaneously utilizing **OpenCV** to detect **ArUco markers** and calculate their exact Z-depth distance in 3D space.

---

## 2. Process Flow

*(How it was built)*

### 🔧 Phase 1: Environment Setup
- Configured a custom Gazebo Ignition simulation world containing the Ares-Nova rover and camera sensors.
- Created a Python script to forge custom 3D geometric cone meshes (`.obj` and `.mtl` files) since Gazebo lacks a built-in cone primitive.

### 📸 Phase 2: Data Collection
- Engineered a ROS 2 camera subscriber node (`aruco_detector.py`) with a manual snapshot feature.
- Drove the rover through the Gazebo world to capture 40+ synthetic images of the custom colored cones under simulation lighting.

### 🧠 Phase 3: AI Training
- Annotated the dataset in **Roboflow** (Red, Green, Blue, Yellow, Orange cones).
- Trained the **YOLOv8 Nano** model locally on an **RTX 4050 GPU** for 50 epochs, achieving a **99.5% mAP50** accuracy.

### 🔗 Phase 4: Sensor Fusion
- Transplanted the compiled AI weights (`best.pt`) into the ROS 2 package.
- Developed the `master_vision.py` node to bridge the Gazebo camera feed to OpenCV, pass the frames through the YOLOv8 model, overlay the ArUco geometry math, and publish the final annotated video feed.

---

## 3. File Structure & Contents

| File / Path | Description |
|---|---|
| `launch/launch_sim.launch.py` | The master launch file. Boots up Gazebo Ignition, spawns the Ares-Nova rover, starts the `robot_state_publisher`, and bridges the ROS 2 / Gazebo message topics. |
| `worlds/world.sdf` | The 3D simulation environment file containing the lighting, physics properties, and the precise spawn coordinates for the geometric cones. |
| `worlds/make_cone.py` | A custom Python geometry script that mathematically generates the vertices, faces, and light-bouncing normal vectors for the 3D cone meshes, exporting them as `.obj` and `.mtl` files. |
| `scripts/aruco_detector.py` | A foundational computer vision node that subscribes to the rover's camera, detects ArUco markers, calculates 3D pose estimation (X, Y, Z distance), and includes a keystroke-triggered dataset collection tool. |
| `scripts/cone_detector.py` | A standalone YOLOv8 inference node used to verify that the neural network was correctly identifying bounding boxes before attempting sensor fusion. |
| `scripts/master_vision.py` | The core **"Unified Visual Cortex"** node. Ingests the raw Gazebo camera feed, runs YOLOv8 to map bounding boxes around colored cones, and simultaneously runs OpenCV pose estimation to draw distance vectors on ArUco markers — displaying the fused result in a single live window. |
| `cone_model.pt` | The fully trained PyTorch neural network weights for the custom cone dataset. |
| `CMakeLists.txt` & `package.xml` | The `ament_cmake` build system configurations required to compile the C++ environment while installing and mapping the Python scripts into the ROS 2 executable paths. |

---

## 4. Obstacles Faced & Engineering Solutions

### Obstacle 1: The NumPy 2.0 Dependency Trap
**Issue:** Ultralytics (YOLO) auto-installed the absolute newest versions of NumPy (2.2) and OpenCV, causing fatal crashes with Ubuntu's built-in Matplotlib library, which required NumPy 1.x.

**Solution:** Surgically downgraded both NumPy (`<2.0.0`) and OpenCV-Python (`<4.10`) to stabilize the environment and synchronize the math libraries.

### Obstacle 2: Gazebo SDF Primitive Limitations
**Issue:** Attempted to use the `<cone>` tag in the `world.sdf` file, resulting in a `"Geometry type [0] not supported"` error.

**Solution:** Discovered Gazebo SDF does not have a cone primitive. Wrote a Python script to mathematically forge a 16-sided custom `.obj` mesh.

### Obstacle 3: The Physics Engine Segfault
**Issue:** When importing the custom `.obj` file, the DART physics engine crashed entirely (Segmentation fault).

**Solution:** Learned the industry standard of separating visuals from collisions. Updated the SDF file so the `<visual>` tag uses the complex `.obj` mesh (for the camera to see), but the `<collision>` tag uses a simple, crash-proof primitive for the physics engine to calculate impacts.

### Obstacle 4: The Unshaded Mesh Phenomenon
**Issue:** The custom 3D cones rendered completely white in Gazebo, ignoring the SDF color tags.

**Solution:** Learned that Gazebo's Ogre2 rendering engine requires custom `.obj` files to bring their own Material Template Library (`.mtl`) files. Rewrote the mesh generation script to bake the RGB colors directly into paired `.mtl` files.

### Obstacle 5: Corrupted Checkpoint Fallback
**Issue:** A `KeyboardInterrupt` (Ctrl+C) corrupted the YOLO training checkpoint. When attempting to resume, YOLO defaulted to the standard COCO8 dataset, resulting in the AI learning to identify horses and dogs instead of traffic cones.

**Solution:** Wiped the corrupted run directories, purged the COCO8 dataset, and initiated a strict, clean training loop using the custom `data.yaml` file.

---

## 5. Key Things Learned

- **ROS 2 Package Architecture** — Deepened understanding of the `ament_cmake` build system, specifically how Python nodes must be housed in a `scripts/` folder, made executable via `chmod`, and explicitly linked in `CMakeLists.txt`.
- **Neural Network Training Loop** — Mastered the end-to-end pipeline of synthetic dataset generation, Roboflow annotation, PyTorch/YOLOv8 hardware acceleration on an RTX GPU, and metric analysis (mAP50).
- **Sensor Fusion** — Successfully combined deep learning (YOLO pixel classification) with classic computer vision geometry (ArUco pose estimation) on a single asynchronous ROS 2 image callback.
- **Simulation Engine Mechanics** — Gained a low-level understanding of how Gazebo Ignition handles rendering vs. physics, specifically the importance of vertex normals for lighting equations and the necessity of simplifying collision meshes to prevent physics engine panics.

---

## 6. Essential Bash Commands (Cheat Sheet)

```bash
#!/bin/bash
# ============================================================
#  Ares-Nova Rover — Command Cheat Sheet
# ============================================================

# ------------------------------------------------------------
#  Workspace Compilation & Setup
# ------------------------------------------------------------

# Clean the build cache
rm -rf ~/ros2_ws/build/ ~/ros2_ws/install/ ~/ros2_ws/log/

# Build a specific package
colcon build --packages-select my_robot_opencv_package

# Source the workspace
source ~/ros2_ws/install/setup.bash


# ------------------------------------------------------------
#  Node Execution
# ------------------------------------------------------------

# Launch the Gazebo simulation
ros2 launch my_robot_opencv_package launch_sim.launch.py

# Run the dataset collector node
ros2 run my_robot_opencv_package aruco_detector.py --ros-args -p use_sim_time:=true

# Run the Unified Visual Cortex node
ros2 run my_robot_opencv_package master_vision.py --ros-args -p use_sim_time:=true


# ------------------------------------------------------------
#  File & Permissions Management
# ------------------------------------------------------------

# Make all scripts executable
chmod +x ~/ros2_ws/src/my_robot_opencv_package/scripts/*.py

# Transfer generated cone meshes into the worlds folder
mv ~/*_cone.obj ~/*_cone.mtl ~/ros2_ws/src/my_robot_opencv_package/worlds/

# Transplant trained AI weights into the ROS 2 package
cp ~/ros2_ws/src/yolo_training/runs/detect/train/weights/best.pt \
   ~/ros2_ws/src/my_robot_opencv_package/cone_model.pt


# ------------------------------------------------------------
#  YOLOv8 AI Training
# ------------------------------------------------------------

# Clear corrupted training cache
rm -rf ~/ros2_ws/src/yolo_training/runs/detect/train*

# Start training on the RTX GPU
yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=50 imgsz=640 device=0
```