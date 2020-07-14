var net = require('net');
var server = net.createServer(function (socket) {
    socket.setEncoding('utf8');
    var d = new Date();
    console.log(d.toISOString(), 'received connection from:', socket.remoteAddress);
    socket.on('data', function (data) {
        var d = new Date();
        console.log(d.toISOString(), 'received data:', data);
        socket.write("you just send me: " + data + "\n");
    });
    socket.on('end', function () {
        var d = new Date();
        console.log(d.toISOString(), 'connection ended.');
    });
});
server.listen(9413);
