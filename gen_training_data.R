rm(list=ls())
source("max_axis.R")
source("get_max.R")


set.seed(350)
acc_window_duration = 1 # seconds
gyo_window_duration = 0.2
partition_n = round(acc_window_duration/gyo_window_duration)
gry_last_n = 2
collor_arr = c("red" , "yellow", "blue" , "green" , "black", "ORANGE")
postur =     c("stand", "left",      "back",  "x",  "right", "stomach")

read_data = read.table("data/raw_data_training2.txt",header=FALSE,sep="," , fill = TRUE)
names(read_data) = c('time_stamp', 'source', 'type' , 'x' , 'y' , 'z')
read_data = data.frame(read_data )

start_line = strtoi(row.names(read_data[read_data$time_stamp == "Sensor set complete.",]))

read_data = read_data[-(1:start_line),]


read_data[,1] = as.numeric(as.character(read_data[,1]))
read_data[,1] = read_data[,1] - as.numeric(as.character(read_data[1,1])) ## remove this later
f<-file("data/training_data2.txt" , "wb")

n = dim(read_data)[1]

time_ptr = read_data[1,1]
end_time = read_data[n,1]

plot(1:n,read_data[,4], type = "l")
plot(1, type="n", xlab="", ylab="" , xlim = c(0,end_time/1000))
v = c()

cnt = 0
last_time_gry = c(rep(c(0,0,0), gry_last_n))
while(time_ptr < end_time){
  x = read_data[(time_ptr  <= read_data$time_stamp) & (read_data$time_stamp < (time_ptr +acc_window_duration*1000)),]
  print(dim(x))
  acc_data = x[x$type== "Acc" & x$source == "wrist",]
  gry_data = x[x$type== "Gry" & x$source == "wrist",]
  target = x[x$type== "Acc" & x$source == "chest",] # temple !!
  
  ## get body posture from chest
  output = max_axis(mean(target$x) , mean(target$y) , mean(target$z))
  print(output)
  points(cnt,1, col = collor_arr[output] , pch = 20)
  
  ## calculate acc data
  acc_feature = cbind(mean(acc_data[,4]), mean(acc_data[,5]), mean(acc_data[,6]))
  
  ## calculate gryo data
  gry_len = dim(gry_data)[1]
  if(gry_len == 0){
    next()
  }
  idx = rep(1:partition_n, each = ceiling( gry_len/ partition_n))
  gry_data_split = split(gry_data, idx[1:gry_len])
  # print(gry_data)
  gry_data_feature = lapply( gry_data_split, function(f) c(mean(f$x) , mean(f$y), mean(f$z)))
  od = get_max_n(gry_data_feature , gry_last_n)
  # print(od)
  
  ## concade acc & gry features
  buf = c(acc_feature, last_time_gry)
  v = c(v,sum(abs(last_time_gry))) # for percentile

  ## write to file  
  writeLines(paste(paste(buf, collapse = ",",sep = ""), postur[output], collapse = "",sep = ","), f)

  last_time_gry = c(gry_data_feature[[od[1]]], gry_data_feature[[od[2]]])
  time_ptr = time_ptr + acc_window_duration*1000
  cnt = cnt + 1
}

close(f)

# plot(read_data[read_data$source == "1" & read_data$type == "Acc",6] , type = "l")


