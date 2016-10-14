var wait1s = ()=>{
  return new Promise(resolve=>setTimeout(resolve,1000))
}

async function waitfor(){
  for(var i=0;i<5;i++){
    await wait1s();
    console.log(i);
  }
}

await waitfor();
await waitfor();
