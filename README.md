# 5g-edge-computing-challenge

Before running python3(version 3.8): needs to install python scripts on Ubuntu 20.
   sudo apt-get install python3-pip
   python3 -m pip install mediapipe
   python3 -m pip install yolov5 
   sudo apt-get install -y libgl1-mesa-de
   python3 -m pip install apscheduler
   python3 -m pip install flask

Video Analysis:
Execute the following sequence from command prompt:   
#1: flask server running:
   1) ./run_flask.sh
   2) open browser and put URL link (IP address:port from the output of 1)
    
#2: Capturing video and running ML, and push the result to flask server:
   1)./run_capture.sh  

#3: Video filese sending: Due to limit, can not load video files, need to send 3 video files
    1) python3 udp_file_send.py --help
       ex:python3 udp_file_send.py --mp4_files practice1.mp4 practice1.mp4 bpm.mp4
       

KPI Analysis:
  1) python3 players_performance_result.py
  2) open browser and put URL link (IP address:port from the output of 1)
 
