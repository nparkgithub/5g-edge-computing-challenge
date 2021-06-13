from socket import *
import time
import sys
import argparse

class ArgmentParser(object):

    def __init__(self):
        pass
    @staticmethod
    def run():
        parser = argparse.ArgumentParser( 
                prog='video_over_udp_sender.py',
                usage='%(prog)s [options] value',
                description='Sending MP4 frame over UDP'
                )
    
        parser.add_argument('--dst_ip_addr', nargs='?', default='127.0.0.1',
                action='store',type=str,
                help='destination ip address(ipv6)')
        parser.add_argument('--dst_port_num', nargs='?', default=5002,
                action='store',type=int,
                help='destination port number')
        parser.add_argument('--packet_length', nargs='?', default=3000,
                action='store',type=int,
                help='packet length')
        parser.add_argument('--packet_interval', nargs='?', default=1,
                action='store',type=float,
                help='packet interval(ms)')
        parser.add_argument('--mp4_files', nargs='*', default=['playing.mp4','throwing.mp4','bpm.mp4'],
                action='store',
                help='MP4 file')
        parser.add_argument('--delta', nargs='?', default=0,type=int,
                action='store',
                help='delta between hoop and player')
        args = parser.parse_args()
        print(f'Input args summary ={args}')
        print(f'IPv6 dst address ={args.dst_ip_addr}')
        print(f'UDP port number ={args.dst_port_num}')
        print(f'Mp4 file to read: {args.mp4_files}')

        return (args)


def main():
    args = ArgmentParser.run()

    clientSocket = socket(AF_INET, SOCK_DGRAM)
    # Opening the audio file
    f_handler = []
    complete_cnt = 0
    serverName = args.dst_ip_addr
    packet_interval = args.packet_interval
    buffer_length = args.packet_length
    port_dict ={}
    for i, video_file in enumerate(args.mp4_files):
        print(f'Opening file ={video_file}')
        _f = open(video_file, "rb")
        f_handler.append(_f)
        port_dict[_f] = args.dst_port_num +i
    start_time = time. time()

    while True:        
        for i, f_h in enumerate(f_handler):
            # Reading the buffer length in data
            data = f_h.read(buffer_length)
            if data:
                port = port_dict[f_h]
                mbps = int(buffer_length * 8 *1000 /packet_interval/(1024 * 1024))
                print(f'sending ={len(data)} bytes to {serverName} {port} every {packet_interval}ms {mbps}mbps')
                clientSocket.sendto(data, (serverName,port))
                if i == 1:
                    delta = args.delta # 2ms more
                else:
                    delta = 0
                #time.sleep((packet_interval + delta)/1000)  # waiting for 0.02 seconds
            else:
                complete_cnt+=1
                f_h.close()
                f_handler.remove(f_h)
        time.sleep((packet_interval + delta)/1000)  # waiting for 0.02 seconds
        if complete_cnt == len(args.mp4_files):
            print(f'{complete_cnt} files read and sent to socket')
            break;

    clientSocket.close()
    end_time = time.time()
    time_elapsed = (end_time - start_time)
    print(f"Sending is complete from UE to AWS!!! {round(time_elapsed)} seconds")
 
if __name__ == "__main__":
    main()
