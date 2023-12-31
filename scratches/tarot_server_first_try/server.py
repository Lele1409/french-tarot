"""The web server for the '*.*/tarot' path"""

import os.path

from flask import Flask, redirect
from flask_socketio import SocketIO

app = Flask('tarot_server',
            # Set where the files are served to the users
            static_url_path='/tarot',
            # Set from where the served files originate
            static_folder=os.path.abspath('public/tarot/static/')
            )

socketio = SocketIO(app)


@app.route('/tarot')
@app.route('/tarot/menu')
def route_tarot_menu():
    """Redirect users from /tarot/menu, to the equivalent menu.html file"""
    return redirect('/tarot/menu.html')


@app.route('/tarot/lobby')
def route_tarot_lobby_id():
    """
    Redirect users from /tarot/lobby, to the equivalent lobby.html file.
    """
    return redirect("/tarot/lobby.html")


@socketio.on('debug')
def lobby_print_debug_msg(msg: str) -> None:
    """
    Receives a message from a websocket and prints it to the console.
    :param msg: A string containing the debug message
    :return: None
    """
    print("Received from lobby websocket: " + msg)


@app.route("/tarot/match/<match_id>")
def route_tarot_match():
    """"""


def run():
    """Runs the app"""

    # TODO: move to production server, don't allow use of unsafe werkzeug
    socketio.run(app, host='0.0.0.0', allow_unsafe_werkzeug=True, debug=True)


if __name__ == '__main__':
    run()
