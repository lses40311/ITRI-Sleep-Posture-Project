# return a list with the dominating axis an its value

max_axis = function(x,y,z){
  arr = array(c(x,y,z))
  arr_abs = abs(arr)
  max_idx = which(arr_abs==max(arr_abs))
  if(arr[max_idx] > 0){
    max_axis = max_idx
  }
  else if(arr[max_idx] < 0){
    max_axis = max_idx + 3
  }
  else{
    max_axis = -1 
  }
}