const socket = io('/lobby');  // imported from the socket.io library
socket.on('connect', () => {
    socket.emit('my event', {data: 'I\'m connected!'});
});