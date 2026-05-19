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
