const startButton = document.getElementById('start-button');


startButton.addEventListener('click', () => {
    // Inform the server that a player want's to start
    websocket.emit('action_game_start');
})


function DEBUG(msg) {
    websocket.emit('manual_debug', {data: msg});
}
