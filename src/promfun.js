function promisify(func){
  return function(){
    var k = arguments;
    return new Promise(function(resolve,reject){
      callback_handler = function(err,back){
        if(err)return reject(err);
        resolve();
      }
      k[k.length.toString()] = callback_handler;
      k.length++;
      func.apply(this,k)
    })
  }
} //turn callback suffixed functions into Promise returning ones.

function runomise(func){
  var restargs = Array.prototype.slice.call(arguments, runomise.length);
  return promisify(func).apply(this,restargs)
} //run any callback suffixed function directly and get Promise for it.

function old_school_wait(interval,callback){
  setTimeout(callback,interval)
}

function promising_wait(interval) {
  return new Promise(function (resolve) {
    old_school_wait(interval,resolve)
  });
}

Promise.resolve()
.then(()=>{
  console.log('start');
  return promisify(old_school_wait)(1000)
})
.then(()=>{
  console.log('run promisified ended');
  return runomise(old_school_wait,1000)
})
.then(()=>{
  console.log('run for promise ended');
  return promising_wait(1000)
})
.then(()=>{
  console.log('hand-packed promise ended');
  old_school_wait(1000,function(){
    console.log('old_school_ended');
  })
})
