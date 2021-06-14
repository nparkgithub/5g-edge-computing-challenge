# 5g-edge-computing-challenge

## Python Package installation
  Before running python3(version 3.8): needs to install python scripts on Ubuntu 20.
   ```bash
   sudo apt-get install python3-pip
   python3 -m pip install mediapipe
   python3 -m pip install yolov5 
   sudo apt-get install -y libgl1-mesa-de
   python3 -m pip install apscheduler
   python3 -m pip install flask
   ```
## Execution 
### Video Analysis Server & Client:
   Execute the following sequence from command prompt:   

#### First, Video analysis Server & Client app:
```bash
   1) open command prompt or a ssm on EC2
   2) ./run_flask.sh
   3) open browser and put URL link (IP address:port from the output of 1)
 ```
  [Video Analytics client APP]( https://photos.app.goo.gl/vDfbTYGWTmHp1wY88)

    
#### Second, Capturing video and running ML, and push the result to flask server:
```bash
   1) open command prompt or a ssm on EC2
   2) ./run_capture.sh  
 ```

#### Third, Video files sending: 
    Due to limit, can not load video files, need to send 3 video files
    If the UE or phone on NOVA, try to use Termux Android app, if it is running on EC2,
```bash
    1) open command prompt or a SSM on EC2, or termux on UE
    2) python3 udp_file_send.py --help
       ex:python3 udp_file_send.py --mp4_files practice1.mp4 practice1.mp4 bpm.mp4
  ```      

### KPI Analysis Client APP:
```bash
  1) open command prompt or a SSM on EC2
  2) python3 players_performance_result.py
  3) open browser and put URL link (IP address:port from the output of 1)

 ```   
 [KPI Analysis Client APP](https://photos.app.goo.gl/7faVS7QAM5rWpwNu6)
