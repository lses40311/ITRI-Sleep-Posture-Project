'''
Train model & and estimates
'''
import scipy as sp
import socket
import sys, os, sched
import csv, string
import numpy as np
import collections as collect
import MySQLdb
import datetime
import extractor
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix


## system parameters
id = 5566
timer_set = False
n_tree = 18
window_size = 50
upload_min = 5
acc_featur_n = 3
gry_feature_n = 6
gry_threshold = 19
postures = ['supine' , 'left_side' , 'right_side' , 'stomatch' , 'stand']
votes = np.zeros(5,dtype = 'int')
cnt = collect.Counter()
schedule = sched.scheduler ( time.time, time.sleep ) 

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

def write2db(conn,cursor,id):
    start_time = (datetime.datetime.now() - datetime.timedelta(minutes=upload_min)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    post = find_max_in_cnt(cnt)
    print 'Writing to SQL db a data: %d,%s,%s,%d' % (id,start_time,end_time,post)
    cursor.execute("INSERT INTO `sleeping`(`ID`, `Start_t`, `End_t`, `Posture`) VALUES (%d,'%s','%s',%d)" % (id,start_time,end_time,post))
    conn.commit()
    return 0

def find_max_in_cnt(cnt):
    max_val = 0
    pos = ''
    for i in cnt:
        if cnt[i] > max_val
        pos = i
    cnt.clear()
    return pos

if len(sys.argv) != 3:
    print 'usage: posture_estimates.py [train data file name] [test data file name]'
    sys.exit()
print 'Connect to SQL sever...'
conn, cursor = connect2db()
print 'Connect SQL db success!'
print 'Loading training data...'
train_data_name = sys.argv[1]
reader = csv.reader(open(train_data_name,'rb'))
x = list(reader)
train_data = np.array(x)
print 'Successfully import %s lines.' % len(train_data)
print 'Loading testing data...'
test_data_name = sys.argv[2]
reader = csv.reader(open(test_data_name,'rb'))
x = list(reader)
test_data = np.array(x)
row_n = len(train_data)
col_n = len(train_data[0,:])
X = train_data[:,0:acc_featur_n]
Y = train_data[:,col_n-1]
X_test = test_data[:,0:acc_featur_n]
Y_test = test_data[:,-1]

print 'Training data size: %d row, %d col' % (row_n,col_n)
print 'Training process for ACC data: %d X %d ...' % (len(X), len(X[0,:]))
all_accuracies = np.zeros(50, dtype = float)
clfs = list()
for i in range(1,50):
    clf_acc = RandomForestClassifier(n_estimators=i)
    clf_acc = clf_acc.fit(X,Y)
    all_accuracies[i] = clf_acc.score(X_test,Y_test)
    clfs.append(clf_acc)
    print 'n_tree = %d, Accuracy = %f.' % (i, all_accuracies[i])
n_tree = np.argmax(all_accuracies)
clf_acc = clfs[n_tree-1]
print 'Done training ACC data model.'
print 'Select n_tree = %d, Accuracy = %f.' % (n_tree, clf_acc.score(X_test,Y_test))
pred_result = clf_acc.predict(X_test)
c_mat = confusion_matrix(Y_test , pred_result, labels=["stand", "back", "right", "left", "stomach"])
print 'Confusion Matrix:'
print "  sd bk rt lf sm"
print c_mat
print 'please press ENTER'
raw_input()

print 'Training process for GYR data: '
for gry_threshold in range(30):
    gry_traing_data = np.empty((0,gry_feature_n+acc_featur_n),float)
    gry_target = np.empty((1,0))
    for d in train_data:
        arr = d[acc_featur_n:(acc_featur_n+gry_feature_n)]
        arr =  arr.astype(float)
        total = sum(abs(arr))
        if(total > gry_threshold):
            gry_traing_data = np.row_stack([gry_traing_data, d[0:(col_n-1)]])
            #gry_target = np.row_stack([gry_target,d[col_n-1]],)
            gry_target = np.append(gry_target, d[col_n-1])
    gry_traing_data = gry_traing_data.astype(float)
    clf_gry = RandomForestClassifier(n_estimators=n_tree)
    clf_gry = clf_gry.fit(gry_traing_data,gry_target)
    print 'GYR threshold = %d, accuracy= %f, sample_number = %d' %(gry_threshold,  clf_gry.score(gry_traing_data, gry_target), len(gry_target))
print 'Done training GYR data model.'

# start realtime predicting
try:
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
    sys.stderr.write("[ERROR] %s\n" % msg[1])
    sys.exit(1)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #reuse tcp
serversocket.bind(('', 55667))
print 'Waiting for client connection...'
serversocket.listen(5)
while True:
    (clientsocket, address) = serversocket.accept()
    print 'Start realtime predictng.'
    while True:
        msg = clientsocket.recv(1024)
        if not msg:
            print 'Disconnect.'
            clientsocket.close()
            break
        else: ## if msg is NOT null
            if not timer_set :
                schedule.enter(120,0,write2db,(conn,cursor,id))
                timer_set = True
            ls = string.split(msg,',')
            ## Star real time predicting
            try:
                test_data = np.array([float(i) for i in ls])
            except ValueError:
                print 'ValueError. Data lose.'
            print '===================================='
            if(sum(abs(test_data[4:])) > gry_threshold):
                gry_result = clf_gry.predict(test_data.reshape(1,-1))
                prob_gry = clf_gry.predict_proba(test_data.reshape(1,-1))
                print 'Predict from GYR: %s\nProbability: %s' % (gry_result[0], np.round(prob_gry[0],3))
            acc_result = clf_acc.predict(test_data[:acc_featur_n].reshape(1,-1))
            prob_acc = clf_acc.predict_proba(test_data[:acc_featur_n].reshape(1,-1))
            ## poling
            if cnt[acc_result] == 0:
                cnt[acc_result] = 1
            else:
                cnt[acc_result] += 1
            print 'Predict from ACC: %s\nProbability: %s' % (acc_result[0], np.round(prob_acc[0], 3))
            print 'postures:    %s' % (clf_acc.classes_)
            print '====================================='
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





