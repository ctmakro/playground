#include <stdio.h>

float pingfang(float x){
  return x*x;
}

int main(){
  printf("pingfang is %f or %d", pingfang(20),(int)(pingfang(40)));

  return 1;
}
