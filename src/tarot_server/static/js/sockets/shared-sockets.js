const websocket = io('/lobby');  // imported from the socket.io library
const playerList = document.getElementById('player-list')
const quitButton = document.getElementById('quit-button')


function homepageRedirect() {
    // First, we get the link from a button that gets the link dynamically
    // assigned
    let url = document.getElementById('menu-nav').href;

    // Then we redirect the user to the found url
    window.location.replace(url);
}


websocket.on('disconnect', () => {
    /* When the websocket disconnects, we want to send the user back
    to the homepage */
    homepageRedirect()
});


websocket.on('info_redirect', (url) => {
    // Redirect the user to the supplied url
    window.location.replace(url);
});


websocket.on('info_room_players', (players) => {
    // Remove all players from the list to add the updated ones
    playerList.innerHTML = ''

    // Fill in with the updated playerList
    Object.entries(players).forEach(([user_id, values]) => {
        // Create an element and update its content to show the player
        let playerElement = document.createElement('li');
        playerElement.textContent = user_id;

        // Set the class of the element depending on the player's state
        if (values['is_replaced']) {
            playerElement.classList.add('player-is-replaced')
        } else if (!(values['is_connected'])) {
            playerElement.classList.add('player-not-connected')
        }

        // Display the element
        playerList.appendChild(playerElement);
    });
});


quitButton.addEventListener('click', () => {
    websocket.emit('action_player_force_quit', () => {
        // Inform the server that the client left the server with intent
    });
    // Redirect the client to the menu
    homepageRedirect();
});
