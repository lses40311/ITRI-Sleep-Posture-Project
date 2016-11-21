import sys, socket
import csv, time
duration = 0.02

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
    sys.stderr.write("[ERROR] %s\n" % msg[1])
    sys.exit(1)

try:
    sock.connect(('127.0.0.1', 55667))
    print 'waiting for accept.'
except socket.error, msg:
    sys.stderr.write("[ERROR] %s\n" % msg[1])
    exit(1)

print 'connection success. start sending data.'
file_name = sys.argv[1]
reader = csv.reader(open(file_name,'rb'))
for idx, line in enumerate(reader):
    if line[1] == 'x' or line[0] == '1':
        pass
    else:
        msg = 'raw_data,'
        msg = msg + str(line[1]) + ',' + str(line[2]) + ',' + str(line[3])
        sock.send(msg)
        print 'send line no. %d.' % idx
        time.sleep(duration)
print 'end of file.'
sock.close()
