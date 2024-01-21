const websocket = io('/lobby');  // imported from the socket.io library


websocket.on('disconnect', () => {
    /* When the websocket disconnects, we want to send the user back
    to the homepage */

    // First, we get the link from a button that gets the link dynamically
    // assigned
    let url = document.getElementById('menu-nav').href

    // Then we redirect the user to the found url
    window.location.replace(url);
});

websocket.on('info_room_players', (players) => {
    console.log(players)

    const playerList = document.getElementById('player-list')

    for (let playerListElement of playerList.children) {
        playerListElement.remove()
    }

    for (let player in players) {
        let playerElement = document.createElement('li')
        playerElement.textContent = player
        playerList.appendChild(playerElement)
    }
});

websocket.on('info_player_replaced', (player_id) => {

});
websocket.on('info_player_removed', (player_id) => {

});


function DEBUG(msg) {
    websocket.emit('manual_debug', {data: msg});
};