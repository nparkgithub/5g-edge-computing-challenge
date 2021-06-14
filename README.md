# 5g-edge-computing-challenge


Video Analysis:
Execute the following sequence:   
#1: flask server running:
   1) ./run_flask.sh
   2) open browser and put URL link (IP address:port from the output of 1)
    
#2: Capturing video and running ML, and push the result to flask server:
   2)./run_capture.sh  

#3: Video filese sending: Due to limit, can not load video files, need to send 3 video files
    1) python3 udp_file_send.py --help
       ex:python3 udp_file_send.py --mp4_files practice1.mp4 practice1.mp4 bpm.mp4
       

KPI Analysis:
  1) python3 players_performance_result.py
  2) open browser and put URL link (IP address:port from the output of 1))
 
