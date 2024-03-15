websocket.on('info_game_event', (data) => {
    console.log('GAME EVENT:');
    console.log(data);
});

function game_event(data) {
    websocket.emit('action_game_event', (data));
}
