'''
Train model & and estimates
'''
import scipy as sp
import socket
import sys
import csv, string
import numpy as np
import MySQLdb
import datetime
import extractor
from sklearn.ensemble import RandomForestClassifier

id = 0
trigger = False
window_size = 50
upload_min = 5
postures = ['supine' , 'left_side' , 'right_side' , 'stomatch' , 'stand']
votes = np.zeros(5,dtype = 'int')

def remove_extra(input_data):
    if input_data[0,1] == 'x' and input_data[1,0] == '1':
        attr_name = input_data[0,]
        input_data = np.delete(input_data,0,0)
        input_data = np.delete(input_data,0,1)
        return attr_name , input_data
    else:
        print 'nothing to remove.'
        return 0,0

def connect2db():
    conn = MySQLdb.connect(host="140.113.203.226",user="ITRI",passwd="ITRINO1",db="Wearable")
    cursor = conn.cursor()
    return conn, cursor

def write2db(conn,cursor,id,post):
    start_time = (datetime.datetime.now() - datetime.timedelta(minutes=upload_min)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print 'Writing to SQL db a data: %d,%s,%s,%d' % (id,start_time,end_time,post)
    cursor.execute("INSERT INTO `sleeping`(`ID`, `Start_t`, `End_t`, `Posture`) VALUES (%d,'%s','%s',%d)" % (id,start_time,end_time,post))
    conn.commit()
    return 0

if len(sys.argv) != 2:
    print 'usage: posture_estimates.py [input csv file name]'
    sys.exit()
print 'Connect to SQL sever...'
conn, cursor = connect2db()
print 'Connect SQL db success!'
train_data_name = sys.argv[1]
reader = csv.reader(open(train_data_name,'rb'))
x = list(reader)
train_data = np.array(x)
print 'Successfully import %s lines.' % len(train_data)
attr_name , train_data = remove_extra(train_data)
row_n = len(train_data)
col_n = len(train_data[1,:])
print 'Training data size: %d row, %d col' % (row_n,col_n)
X = train_data[0:row_n,0:(col_n-1)]
Y = train_data[:,col_n-1]
clf = RandomForestClassifier(n_estimators=10)
clf = clf.fit(X,Y)
print 'Done training model.'

# start realtime predicting
try:
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
    sys.stderr.write("[ERROR] %s\n" % msg[1])
    sys.exit(1)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #reuse tcp
serversocket.bind(('', 55667))
serversocket.listen(5)
while True:
    feature_gen = extractor.Features(window_size)
    (clientsocket, address) = serversocket.accept()
    while True:
        msg = clientsocket.recv(1024)
        if not msg:
            print 'Disconnect.'
            clientsocket.close()
            break
        else: # if it is NOT null
            ls = string.split(msg,',')
            if ls[0] == 'raw_data': # raw data
                flag, feature_x, feature_y, feature_z = feature_gen.add_data(ls[1],ls[2],ls[3])
                if flag == 1:
                    test_data = np.array([feature_x,feature_y,feature_z])
                    test_data = test_data.reshape(1,-1)
                    result = clf.predict(test_data)
                    result = result.tolist()
                    print 'Output posture: %s.' % postures[int(result[0])]
                    votes[int(result[0])] += 1
                    if datetime.datetime.now().minute % upload_min == 0 and trigger :
                        post_vote = votes.argmax(axis=0)
                        write2db(conn,cursor,id,post_vote)
                        id += 1
                        trigger = False
                    elif datetime.datetime.now().minute % upload_min != 0:
                        trigger = True
            else:
                print 'other data.'
conn.close()

'''
# predicting test
print 'Start testing.'
test_data_name = sys.argv[2]
reader = csv.reader(open(test_data_name,'rb'))
x = list(reader)
test_data = np.array(x)
attr_name , test_data = remove_extra(test_data)
print 'Import testing data done.'

total = len(test_data)
groud_truth = test_data[:,3]
test_data = test_data[:,0:3]
result = clf.predict(test_data)
print 'Testing done.'
#print np.array(groud_truth)
#print result
cnt = 0
for i in range(total):
    if groud_truth[i] == result[i]:
        cnt = cnt + 1
print 'Accuracy = %.3f' %  (float(cnt)/float(total))
'''





