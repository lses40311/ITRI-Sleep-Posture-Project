import numpy as np
import csv
from sklearn.model_selection import train_test_split

## Paths
data_path  = 'data/demo_training_data.txt'

## Parameters
labels = ["stand", "back", "right", "left", "stomach"]
validation_portion = 0.33

reader = csv.reader(open(data_path,'rb'))
x = list(reader)
labeled_data = np.array(x)
data_dim = labeled_data.shape

idx_list = list() 

for label in labels:
    idx = labeled_data[:,-1] == label
    idx_list.append(idx)

data_by_class = list()
lens = list()
for idx in idx_list:
    class_data = labeled_data[idx,:]
    data_by_class.append(class_data)
    lens.append(class_data.shape[0])

training_data = validation_data = np.empty([0,data_dim[1]])
for class_data in data_by_class:
    train, valid = train_test_split(class_data, test_size=validation_portion, random_state=42)
    training_data = np.vstack((training_data, train))
    validation_data = np.vstack((validation_data, valid))

# training_data.astype('S32')
np.savetxt("training_data.csv", training_data,fmt='%s', delimiter=",")
np.savetxt("validation_data.csv", validation_data,fmt='%s', delimiter=",")

print idx_list
print len(idx_list)
print data_by_class[2]
print lens
print data_dim
print training_data.dtype
