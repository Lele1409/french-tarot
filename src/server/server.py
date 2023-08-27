"""The server for the '/tarot' path"""

import os.path
from flask import Flask
from werkzeug.utils import redirect

app = Flask(__name__,
            # Set where the files are served to the users
            static_url_path='/tarot',
            # Set from where the served files originate
            static_folder=os.path.abspath('public/tarot/static/')
            )


@app.route('/tarot/game')
def route_tarot_game():
    """Redirect users from /tarot/game, to the equivalent game.html file"""
    return redirect('/tarot/game.html')


@app.route('/tarot/lobby')
def route_tarot_lobby_id():
    """
    Redirect users from /tarot/lobby, to the equivalent lobby.html file.
    """
    return redirect("/tarot/lobby.html")


@app.route("/tarot/match/<match_id>")
def route_tarot_match():
    """"""

def run_app():
    """Runs the app"""
    app.run()
