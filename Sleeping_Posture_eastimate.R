rm(list=ls()) ;
source('max_axis.R')
library(randomForest)
library(rpart)
library(pmml)
set.seed(350)
window_size = 70

read_data = read.table("Data/output.txt",header=FALSE,sep=",")
names(read_data) = c('source' , 'x' , 'y' , 'z')
summary(read_data)

flag = FALSE
rounds = floor(nrow(read_data) / window_size)
index = ((1:rounds) -1) * window_size +1
feature_data = matrix(0,nrow=0,ncol=4,dimnames =NULL) 
colnames(feature_data) = c('x' , 'y' , 'z', 'class')

posture = -1

for(i in index){
  window_data = read_data[i:(i+window_size-1),]
  chest_data = subset(window_data, window_data$source == 1)
  if(nrow(chest_data) != 0){
    chest_data = apply(chest_data, 2,mean)
    posture = max_axis(chest_data[2],chest_data[3],chest_data[4])
    feature_data = rbind(feature_data, append(chest_data[2:4],posture))
  }
  else{
    #print('skip')
  }
}

######## write csv ########
write.csv(feature_data, file = "Output/training_data.csv")

####### spliting data ########
index = sample(2,nrow(feature_data),replace = TRUE,prob = c(0.7,03))
train_split = feature_data[index ==1,]
test_split = feature_data[index==2,]
write.csv(train_split, file = "Output/training_split.csv")
write.csv(test_split, file = "Output/test_split.csv")

######## Random Forest ########
fit <- randomForest(as.factor(class) ~ x + y + z ,
                   data=feature_data,
                   importance=TRUE,
                   ntree=10)

plot(fit, log="y")
# model_output = pmml(fit, fit.name="randomForest_Model",
#                    app.name="Rattle/PMML",
#                    description="Random Forest Tree Model",
#                    copyright=NULL, transforms=NULL, unknownValue=NULL)
#write(toString(model_output),file = "Output/model_RF.pmml")

data=data.frame(feature_data)
data[,4] = as.factor(data[,4])
######### Decision Tree ########
fit_DT <- rpart(class ~ x + y + z,
             data = data ,
             method="class")
model_output = pmml(fit_DT, model.name="RPart_Model",
     app.name="Rattle/PMML",
     description="RPart Decision Tree Model", copyright = NULL)
write(toString(model_output),file = "Output/model_DT.pmml")



