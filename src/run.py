"""THIS FILE RUNS THE COMMAND FOR STARTING THE SERVER.
There is no need to start anything else than the server,
at the time of writing, since all other events start through
user interaction on the website"""

from src.tarot_server.server import run_tarot_server

if __name__ == "__main__":
	run_tarot_server()
