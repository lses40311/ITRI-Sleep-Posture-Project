sumabs = function(i){
  sumabs = sum(abs(c(i)))
}

get_max_n = function(l, n){
  len = length(l)
  avg = lapply(l, sumabs)
  # arr = c()
  # for(i in l){
  #   print(class(i$x))
  #   arr = c(arr, sum(abs(c(i$x , i$y , i$z))))
  # }
  print(len)
  or = order(unlist(avg) , decreasing=TRUE)[1:n]
  get_max_n = or
}