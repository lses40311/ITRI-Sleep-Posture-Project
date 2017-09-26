from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname
import time

def get_ip_address():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def broadcast(MAGIC, my_ip, udp_port):
    s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
    s.bind(('', 0))
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #this is a broadcast socket
    # my_ip = get_ip_address()
    print 'Broadcast server IP: ' + my_ip
    while 1:
        data = MAGIC+'=' + my_ip + '='
        s.sendto(data, ('<broadcast>', udp_port))
        time.sleep(5)





