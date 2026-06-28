import cv2
try:
    import cv2.aruco as aruco
    try:
        dictionary = aruco.Dictionary_get(aruco.DICT_5X5_250)
        img = aruco.drawMarker(dictionary, 42, 500)
    except AttributeError:
        dictionary = aruco.getPredefinedDictionary(aruco.DICT_5X5_250)
        img = aruco.generateImageMarker(dictionary, 42, 500)
    cv2.imwrite('/home/yashvant/ros2_ws/src/my_robot_opencv_package/worlds/aruco_marker.png', img)
    print("SUCCESS: Marker successfully generated and saved!")
except Exception as e:
    print(f"FAILED: {e}")
