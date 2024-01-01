"""Allows other modules to all access the same configuration files.
With the use of overwrite_config_dir also allows you to override the
path where the config gets stored."""

# TODO: add verification for config checking that all values that are
#  in the config are also valid for their purpose

import configparser
import os
from typing import AnyStr

# Set the default path for where to look for the config files
DEFAULT_CONFIG_DIR_PATH: os.PathLike[AnyStr] | str = (
		os.path.dirname(__file__) + '\\'
)

# Initialize variables at module level to None
config_tarot_server: configparser.ConfigParser | None = None
config_tarot_game: configparser.ConfigParser | None = None


def overwrite_config_dir(path=DEFAULT_CONFIG_DIR_PATH) -> bool:
	"""Set where the config file is loaded from.
	:param path: Path pointing to the config file
	 (consider using an absolute path)
	:returns True if all config files were found, False otherwise"""

	# Set new directory
	current_file_dir = path

	# Magic value: contains the names of all the config files
	file_names = ['tarot_server.cfg', 'tarot_game.cfg']

	# Modify the variables/values stored at module level
	global config_tarot_server
	global config_tarot_game

	# Get the config data from the files with the paths specified
	# Works also if the files do not exist
	config_tarot_server = configparser.ConfigParser()
	config_tarot_server.read(current_file_dir + file_names[0])

	config_tarot_game = configparser.ConfigParser()
	config_tarot_game.read(current_file_dir + file_names[1])

	# ConfigParser.read() returns a list containing all the files that were
	# successfully loaded. Checks if all files were successfully loaded by
	# verifying the content of the return values.
	return bool(
		config_tarot_server.read(current_file_dir + file_names[0])
		and
		config_tarot_game.read(current_file_dir + file_names[1])
	)


# Get config files from default config location
overwrite_config_dir()
