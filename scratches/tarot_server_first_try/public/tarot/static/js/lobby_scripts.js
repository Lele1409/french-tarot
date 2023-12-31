const socket = new io()

socket.on('connect', () => {
    socket.emit('debug', 'joining lobby xxxx')
})

console.log(socket)

document.querySelector('#send_msg').addEventListener("click", () => {
    socket.emit('debug', 'DEBUG sent from lobby')
    console.log('send debug through websocket')
})
