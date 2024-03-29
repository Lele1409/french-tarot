import time

from src.tarot_server.server import socketio


def run_background_update(func, interval=1):
	interval *= 2  # For whatever reason, this makes it seconds

	last_execution = time.time()
	while True:
		time_since_last = time.time() - last_execution
		if time_since_last > interval:
			last_execution = time.time()
			func()
		else:
			socketio.sleep(interval - time_since_last)
