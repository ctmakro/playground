#include <iostream>
#include <vector>

using namespace std;

class Exposure{
public:
  int value;
  int applied_value;

  vector<int> list;

  Exposure(){
    value = 0;
    applied_value = 0;
  }

  void set(int val){
    value = val;
    apply();
    list.push_back(val);
  }

  void apply(){
    applied_value = value*2;
  }
};

int main(int argc, char** argv){
  Exposure e;

  e.set(6);
  e.set(13);
  auto i = e.list.begin();
  while(i!=e.list.end()){
    cout << *i << ", "; i++;
  }

  e.set(9);

  i = e.list.begin();
  while(i!=e.list.end()){
    cout << *i << ", "; i++;
  }

  cout << "hello world!";
  e.apply();
  cout << e.applied_value << endl;
  return 0;
}
