const websocket = io('/lobby');  // imported from the socket.io library

websocket.on('connect', () => {
    websocket.emit('my event', {data: 'I\'m connected!'});
});

function DEBUG(msg) {
    websocket.emit('MANUAL_DEBUG', {data: msg})
}