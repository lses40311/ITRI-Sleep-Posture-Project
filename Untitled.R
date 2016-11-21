rm(list=ls())
source("max_axis.R")


set.seed(350)
acc_window_duration = 1 # seconds
gyo_window_duration = 0.2
partition_n = acc_window_duration/gyo_window_duration
collor_arr = c("red" , "yellow" , "blue" , "green" , "black")

read_data = read.table("data/raw_data_7_23.txt",header=FALSE,sep="," , fill = TRUE)
names(read_data) = c('time_stamp', 'source', 'type' , 'x' , 'y' , 'z')
read_data = data.frame(read_data )

start_line = strtoi(row.names(read_data[read_data$time_stamp == "Sensor set complete.",]))

read_data = read_data[-(1:start_line),]


read_data[,1] = as.numeric(as.character(read_data[,1]))
read_data[,1] = read_data[,1] - 1479727444952 ## remove this later

n = dim(read_data)[1]

time_ptr = read_data[1,1]
end_time = read_data[n,1]

# plot(1:n,read_data[,4], type = "l")
# plot(1, type="n", xlab="", ylab="" , xlim = c(0,end_time/1000))

cnt = 0
while(time_ptr < end_time){
  x = read_data[(time_ptr  <= read_data$time_stamp) & (read_data$time_stamp < (time_ptr +1000)),]
  print(dim(x))
  acc_data = x[x$type== "Acc" & x$source == "wrist",]
  gyo_data = x[x$type== "Gyo" & x$source == "wrist",]
  target = x[x$type== "Acc" & x$source == "1",] # temple !!
  
  output = max_axis(mean(target$x) , mean(target$y) , mean(target$z))
  # print(output)
  # points(cnt,1, col = collor_arr[output] , pch = 20)
  
  time_ptr = time_ptr + acc_window_duration*1000
  cnt = cnt + 1
}

plot(read_data[read_data$source == "1" & read_data$type == "Acc",6] , type = "l")


