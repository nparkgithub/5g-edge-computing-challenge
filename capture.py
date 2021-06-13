# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 18:57:44 2019

@author: seraj
"""
import time
import cv2 
import threading 
import sys
import socket
import mediapipe as mp
import time
import math
import json
from ball_detect import yolov5_main
MAX_BUFFER = 10*1024*1024 # 10 MB bytes
input_stream_address_internal = "127.0.0.1" # internal 
input_stream_address_external = "0.0.0.0"   # external 

class poseDetector():

    def __init__(self, mode=False, upBody=False, smooth=True,
                 detectionCon=0.5, trackCon=0.5):

        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.upBody, self.smooth,
                                     self.detectionCon, self.trackCon)

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                try:
                    self.mpDraw.draw_landmarks(img, self.results.pose_landmarks,
                                       self.mpPose.POSE_CONNECTIONS)
                except:
                    pass
        return img

    def findPosition(self, img, draw=True):
        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                # print(id, lm)
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.lmList

def move_distance(pre_pos, new_pos):
    distance = math.sqrt((new_pos[0]-pre_pos[0])**2 + (new_pos[1]-pre_pos[1])**2)
    return distance

def run_hoop_algorithm():
    yolov5_main(['--source','udp://127.0.0.1:5002', '--weights', 'yolov5s.pt', '--conf', '0.25'])

def run_pos_algorithm():
    in_address = 'udp://127.0.0.1:5003' 
    out_address = "127.0.0.1"
    out_port = 6003
    cap = cv2.VideoCapture(in_address,cv2.CAP_FFMPEG)
    s = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM,socket.IPPROTO_UDP) # UDP
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,MAX_BUFFER)
    pTime = 0
    detector = poseDetector()
    pre_pos = [0,0]
    new_pos = [0,0]
    #pre_time = time.clock()
    pre_time = time.time()
    right_shoulder_cnt = 0
    first_time = True
    """ Report message """
    pose_algo_report = {'report_id': 'pose_algo', 'attempt': 0, 'shoulder':[[0,0],[0,0]], 'elbow':[[0,0],[0,0]]}
    report_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,socket.IPPROTO_UDP)
    report_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    report_address_port = ('127.0.0.1',7002)
    while True:
        success, img = cap.read()
        if success == False:
            print('Something wrong to read from video')
            break
        img = detector.findPose(img)
        lmList = detector.findPosition(img, draw=False)
        if len(lmList) != 0:
            #Elbow
            #print(lmList[13])
            cv2.circle(img, (lmList[13][1], lmList[13][2]), 15, (0, 0, 255), cv2.FILLED)
            elbow_left_pos = [lmList[13][1], lmList[13][2]] 
            #print(lmList[14])
            cv2.circle(img, (lmList[14][1], lmList[14][2]), 15, (0, 0, 255), cv2.FILLED)
            elbow_right_pos = [lmList[14][1], lmList[14][2]]
            pose_algo_report['elbow'] =[[elbow_left_pos],[elbow_right_pos]] 
           

            #print(lmList[11])
            #Shoulder
            cv2.circle(img, (lmList[11][1], lmList[11][2]), 15, (255, 0, 0), cv2.FILLED)
            #print(lmList[12])
            cv2.circle(img, (lmList[12][1], lmList[12][2]), 15, (255, 0, 0), cv2.FILLED)
            shoulder_left_pos = [lmList[11][1], lmList[11][2]]
            shoulder_right_pos =[lmList[12][1], lmList[12][2]]  
            pose_algo_report['shoulder'] =[[elbow_left_pos],[elbow_right_pos]] 

            # attempt calculation based on right shoulder up 
            new_pos = [lmList[12][1], lmList[12][2]] 
            if time.time() - pre_time > 3:
                distance = move_distance(pre_pos, new_pos)
                print(f'distance={distance:.2f}')
                pre_time = time.time()
                pre_pos = new_pos
                if distance > 500:
                    if first_time == False:
                        right_shoulder_cnt+=1
                        print(f'swig count ={right_shoulder_cnt}')
                        pose_algo_report['attempt'] = right_shoulder_cnt
                    first_time = False
                json_dumps = json.dumps(pose_algo_report)
                report_socket.sendto(bytes(json_dumps,encoding="utf-8"), report_address_port)    

        
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 0), 3)

        #cv2.imshow("Image", img)
        #cv2.waitKey(1)
        img = cv2.resize(img, (0,0), fx=0.1, fy=0.1) 
        frame = cv2.imencode('.jpg', img)[1].tobytes()
        s.sendto( frame, (out_address, out_port))
        #yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        print(f'capture_pose_algo ={len(frame)}')

    cap.release()
    cv2.destroyAllWindows()
    


def capture_hoop():   
    in_address = 'udp://127.0.0.1:5002' 
    out_address = "127.0.0.1"
    out_port = 6002
    cap1 = cv2.VideoCapture(in_address,cv2.CAP_FFMPEG)
    s = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM,socket.IPPROTO_UDP) # UDP
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,MAX_BUFFER)
    while(cap1.isOpened()):
      # Capture frame-by-frame
        ret, img = cap1.read()
        print(f'capture_hoop : {in_address}')
        if ret == True:
            img = cv2.resize(img, (0,0), fx=0.1, fy=0.1) 
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            #yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            print(f'capture_hoop={len(frame)}')
            #cv2.imshow('capture_hoop',img)
            s.sendto( frame,(out_address, out_port))
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break
        else: 
            break
    
def capture_pose():
    in_address = 'udp://127.0.0.1:5003'
    out_address = "127.0.0.1"
    out_port = 6003
    cap2 = cv2.VideoCapture(in_address,cv2.CAP_FFMPEG)
    s = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM,socket.IPPROTO_UDP) # UDP
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,MAX_BUFFER)
    # Read until video is completed
    while(cap2.isOpened()):
      # Capture frame-by-frame
        ret, img = cap2.read()
        print(f'capture_pose : {in_address}')
        if ret == True:
            img = cv2.resize(img, (0,0), fx=0.1, fy=0.1) 
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            s.sendto( frame, (out_address, out_port))
            #yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            print(f'capture_pose ={len(frame)}')
            #cv2.imshow('capture_pose',img)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break
        else: 
            cap2.release()
            cv2.destroyAllWindows()
            break

def capture_bpm():
    in_address = 'udp://127.0.0.1:5004'
    out_address = "127.0.0.1"
    out_port = 6004
    cap3 = cv2.VideoCapture(in_address,cv2.CAP_FFMPEG)
    s = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM,socket.IPPROTO_UDP) # UDP
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,MAX_BUFFER)
    # Read until video is completed
    while(cap3.isOpened()):
      # Capture frame-by-frame
        ret, img = cap3.read()
        print(f'capture_bpm : {in_address}')
        if ret == True:
            img = cv2.resize(img, (300,500)) 
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            #yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            s.sendto( frame, (out_address, out_port))
            print(f'capture_bpm ={len(frame)}')
            #cv2.imshow('capture_bpm',img)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break
        else: 
            cap3.release()
            cv2.destroyAllWindows()
            break



if __name__ == "__main__":
    # creating thread
    print(f'python capture [hoop, hoop_algo, pos,pose_algo,bpm]')
    if sys.argv[1] == 'hoop':
        t1 = threading.Thread(target=capture_hoop)
    elif sys.argv[1] == 'hoop_algo':
        t1 = threading.Thread(target=run_hoop_algorithm)
    elif sys.argv[1] == 'pose':
        t1 = threading.Thread(target=capture_pose)
    elif sys.argv[1] == 'pose_algo':
        t1 = threading.Thread(target=run_pos_algorithm)
    elif sys.argv[1] == 'bpm':
        t1 = threading.Thread(target=capture_bpm)
  
    t1.daemon = True
  
    t1.start()
 
  
    # wait until thread 1 is completely executed
    t1.join()
    # wait until thread 2 is completely executed
 
  
    # both threads completely executed
    print("Done!")
