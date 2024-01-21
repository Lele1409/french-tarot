const websocket = io('/lobby');  // imported from the socket.io library

websocket.on('connect', () => {});

function DEBUG(msg) {
    websocket.emit('manual_debug', {data: msg})
}