const startButton = document.getElementById('start-button')


startButton.addEventListener('click', () => {
    websocket.emit('action_game_start', () => {
        // Inform the server that a player want's to start
    });
})


function DEBUG(msg) {
    websocket.emit('manual_debug', {data: msg});
}