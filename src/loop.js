function wait(t){
  return new Promise(function(res,rej){
    setTimeout(res,t);
  })
}

function loop(times,fn){

  function inloop(invtimes){
    if(invtimes<times){
      fn(invtimes)
      .then(()=>{
        inloop(invtimes+1);
      })
    }
  }

  inloop(0);
}

loop(300,function(times){
  return wait(0)
  .then(()=>{
    console.log(times);
  });
});
