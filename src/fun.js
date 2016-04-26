require('traceur');

console.log('helloworld');

function promise_wait(interval) {
  return new Promise(function (resolve) {
    setTimeout(resolve, interval);
  });
}

function traditional_wait(interval, callback) {
  setTimeout(callback, interval);
}

async function async_wait(timeout) {
  return new Promise((resolve, reject) => {
    setTimeout(function() {
      resolve();
    }, timeout);
  });
};

promise_wait(1000).then(function () {
  console.log('after 1s');
  return promise_wait(1000);
}).then(function () {
  console.log('after 2s');
  return promise_wait(1000);
}).then(function () {
  console.log('after 3s');
  return promise_wait(1000);
}).then(function () {
  console.log('after 4s');
  traditional_wait(1000, function () {
    console.log('after 5s');
    traditional_wait(1000, function () {
      console.log('after 6s');
      traditional_wait(1000, function () {
        console.log('after 7s');

        (async function() {
          for(var i = 8; i<10; i++){
            await async_wait(1000);
            console.log('after '+i+'s');
          }
        })()

      });
    });
  });
});
