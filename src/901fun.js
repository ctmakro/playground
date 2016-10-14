var net = require('net');

var socket = net.connect(1901,'10.0.0.91',()=>{
  console.log('conn successful');
  socket.setEncoding('utf8');

  socket.on('data',function(data){
    console.log(data);
  })

  socket.on('error',function(err){
    console.log(err);
  })

  socket.write('Date\n')
  socket.write('Press Get\n')
  socket.write('Press Get\n')
  socket.write(' tEMP\n')
})
