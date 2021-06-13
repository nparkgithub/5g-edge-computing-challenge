# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 18:57:44 2019

@author: seraj
"""
import time
import cv2 
import socket
from flask import Flask, render_template, Response, g, jsonify
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import json
""" Linux
import fcntl, os
"""
import errno


app = Flask(__name__)
MAX_DGRAM = 2**16
MAX_BUFFER = 10*1024*1024 # 10 MB bytes
server_ip = "127.0.0.1"
report = { 'attempt':0, 'success': 0, 'fail':0}
hoop_report_data = {'attempt':0,'location':0}
""" pose and hoop algorithm report the result of ML"""
report_address_port = ('127.0.0.1',7002)
report_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
report_s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,MAX_BUFFER)
report_s.setblocking(0)
report_s.bind(report_address_port)

""" For linux
fcntl.fcntl(report_s, fcntl.F_SETFL, os.O_NONBLOCK)
"""
def capture_report():   
    global report
    global hoop_report_data
    try:
        msg = report_s.recv(MAX_DGRAM)
    except socket.error as e:
        err = e.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
            print('No data available')
        else:
            # a "real" error occurred
            print(e)
            sys.exit(1)
    else:
        print(f'got message :{msg} {len(msg)} bytes')
        msg = msg.decode("utf-8")
        msg = json.loads(msg)
        try:
            if msg["report_id"] == 'pose_algo':
                report = msg
            else:
                hoop_report_data = msg
        except:
            sys.exit(1)
            pass

        # got a message, do something :)
        """
        report['attempt'] +=1
        report['success'] = report['attempt'] -1
        report['fail'] = report['attempt'] - report['success']  """
        print(f'{report}')


sched = BackgroundScheduler(daemon=True)
sched.add_job(capture_report,'interval',seconds=3)
sched.start()



@app.route('/')
def index():
    """Video streaming home page."""
    current_time = str(datetime.now())
    return render_template('index.html',datetime = current_time )


# Hoop video
def gen_hoop():
    """Video streaming generator function."""
    #cap = cv2.VideoCapture('768x576.avi')
    # Create a UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,MAX_BUFFER)
    # Bind the socket to the port
    server_address = (server_ip, 6002)
    print(f'udp hoop ={server_address})')
    s.bind(server_address)
    while s:
         frame, address = s.recvfrom(MAX_DGRAM)
         print(f'hoop frame={len(frame)}')
         yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    #cap1 = cv2.VideoCapture('udp://127.0.0.1:5002',cv2.CAP_FFMPEG)
    cap1.set(cv2.CAP_PROP_BUFFERSIZE, 1);
    
    # Read until video is completed
   
    while(cap1.isOpened()):
      # Capture frame-by-frame
        ret, img = cap1.read()
        if ret == True:
            img = cv2.resize(img, (0,0), fx=0.1, fy=0.1) 
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            #time.sleep(0.1)
        else: 
            break
# Pose video    
def gen_pose():
    """Video streaming generator function."""
    #cap = cv2.VideoCapture('golf.mp4')
    #cap2 = cv2.VideoCapture('udp://127.0.0.1:5003',cv2.CAP_FFMPEG)
    # Create a UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,MAX_BUFFER)
    # Bind the socket to the port
    server_address = (server_ip, 6003)
    print(f'udp pose ={server_address})')
    s.bind(server_address)
    while s:
         frame, address = s.recvfrom(MAX_DGRAM)
         print(f'pose frame={len(frame)}')
         yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Read until video is completed
    while(cap2.isOpened()):
      # Capture frame-by-frame
        ret, img = cap2.read()
        print('gen2')
        if ret == True:
            img = cv2.resize(img, (0,0), fx=0.1, fy=0.1) 
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            #time.sleep(0.01)
        else: 
            break
# BPM video
def gen_bpm():
    """Video streaming generator function."""
    #cap = cv2.VideoCapture('golf.mp4')
    #cap2 = cv2.VideoCapture('udp://127.0.0.1:5003',cv2.CAP_FFMPEG)
    # Create a UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,MAX_BUFFER)
    # Bind the socket to the port
    server_address = (server_ip, 6004)
    print(f'udp bpm ={server_address})')
    s.bind(server_address)
    while s:
         frame, address = s.recvfrom(MAX_DGRAM)
         print(f'bpm frame={len(frame)}')
         yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Read until video is completed
    while(cap3.isOpened()):
      # Capture frame-by-frame
        ret, img = cap3.read()
        print('gen2')
        if ret == True:
            #img = cv2.resize(img, (0,0), fx=0.1, fy=0.1) 
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            #time.sleep(0.01)
        else: 
            break

@app.route('/video_hoop')
def video_hoop():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_hoop(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_pose')
def video_pose():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_pose(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_bpm')
def video_bpm():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_bpm(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/timer')
def timer():
    datumpy = datetime.now()
    datumpy = datumpy.strftime("%Y-%m-%d %H:%M:%S")
    print(datnumpy)
    return jsonify(result=datumpy)


@app.route('/price')
def price():
    # obtain jsonify from Flask: from flask import jsonify
    # you may change the output/format as you need
    datumpy = datetime.now()
    datumpy = datumpy.strftime("%Y-%m-%d %H:%M:%S")
    datumpy = datumpy + ' ' + json.dumps(report)
    return jsonify({'value': datumpy})

@app.route('/hoop_report')
def hoop_report():
    # obtain jsonify from Flask: from flask import jsonify
    # you may change the output/format as you need
    datumpy = datetime.now()
    datumpy = datumpy.strftime("%Y-%m-%d %H:%M:%S")
    datumpy = datumpy + ' ' + json.dumps(hoop_report_data)
    return jsonify({'value': datumpy})

@app.before_request
def before_request():
   g.request_start_time = time.time()
   g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)
