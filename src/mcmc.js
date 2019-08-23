var in_c = (x,y)=>(x*x+y*y)<1.0
var in_r = (x,y)=>{d=(x*x+y*y);return d<1.0 && d>0.9801}
var range = x=>{
  k = []
  for(i=0;i<x;i++){
    k.push(i)
  }
  return k
}
var pow = Math.pow,log=Math.log,e=Math.exp
var draw = ()=>r()*2-1
var print = console.log
var crypto = require('crypto');

var rbgen = ()=>{
  var randoms = []

  var batch=10240
  var fill=()=>{
    b = crypto.randomBytes(batch*4)
    for(var i =0;i<batch;i++){
      randoms[i] = (b.readUInt32LE(i*4)/(65536*65536))
    }
    idx=0
  }

  var idx=0

  var get = ()=>{
    if(idx>=batch){
      fill()
    }
    return randoms[idx++]
  }

  fill()

  return get
}

var r = rbgen()

function simonce(times){
  var inc=0
  var all=times

  for (var i = 0; i < all; i++) {
    var x = draw()
    var y = draw()
    inc += in_c(x,y)?1:0
  }

  var pi = inc/all*4
  var pcdiff = (pi-Math.PI)/Math.PI
  // print(diff.toFixed(5), pi)
  return pcdiff
}

function simring(times){
  var inr = 0
  var all = times
  for(var i=0;i<all;i++){
    var x = draw()
    var y = draw()
    inr += in_r(x,y)?1:0
  }

  var ringarea = inr/times*4
  var realarea = (Math.PI*(1-0.9801))
  var pcdiff = (ringarea - realarea)/realarea
  return pcdiff
}

function fold(i){
  while(i>1)i=i-2;
  while(i<-1)i=i+2;
  return i
}
function dist(x1,y1,x2,y2){
  return Math.sqrt(pow(x1-x2,2)+pow(y1-y2,2))
}

function simring_mcmc(times){
  var inr = 0
  var all = times

  var x = draw()
  var y = draw()
  var last_inr = in_r(x,y)

  while(all){
    var thisx = fold(x+draw()/10)
    var thisy = fold(y+draw()/10)
    var this_inr = in_r(thisx,thisy)

    thisp = this_inr?e(1):1
    lastp = last_inr?e(1):1

    var prob = thisp/lastp

    if(r()<prob){

      x = thisx
      y = thisy

      last_inr = this_inr

    }else{
      //stay
    }

    inr += last_inr?1:0
    all--
  }

  var ringarea = inr/times*4
  var realarea = (Math.PI*(1-0.9801))
  var pcdiff = (ringarea - realarea)/realarea
  return pcdiff
}

function smpling_var(f,times){
  var diffhist=[]
  for(var k = 0;k<10;k++){
    // print('trying',times,'times:')
    var diff = f(times)
    diffhist.push(diff)
  }
  var mean = diffhist.reduce((a,b)=>a+b)/diffhist.length

  var variance =
  diffhist.map((a)=>{a-=mean;return a*a}).reduce((a,b)=>a+b)/diffhist.length

  print('mean,variance',mean,variance)
}

// smpling_var(simonce,100)
for(i in range(10)){
  smpling_var(simring,10000)
}
print('---mcmc---')
for(i in range(10)){
  smpling_var(simring_mcmc,10000)
}
