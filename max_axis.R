# return a list with the dominating axis an its value

max_axis = function(x,y,z){
    if(abs(x) > abs(y) ){
      if(abs(x) > abs(z)){
        max = 1
        winning_point = x
      }
      else{
        max = 3
        winning_point = z
      }
    }
    else{
      if(abs(y) > abs(z)){
        max = 2
        winning_point = y
      }
      else{
        max = 3
        winning_point = z
      }
    }
  max_axis = max
}