"""
Allows easy access to config files.
Implements loading, simple validation, and accessing of configuration data.
"""

import configparser
import os
import re
from pathlib import Path
from typing import AnyStr

# Set the default path for the config files
DEFAULT_CONFIG_DIR_PATH: os.PathLike[AnyStr] | str = (
        os.path.dirname(__file__) + '\\'
)

# Set regular expressions for the validation
REG_EXP_BOOLEAN = r"^(true|false)(?!(true|false))$"
REG_EXP_LIST = r"^(\w+)(?:\|(\w+))*$"


class Config:
    """
    A class that contains all the configuration data set in the configuration
    files.
    It also validates all data entered into the configuration files against
    their respective domains determined by regexp.
    """
    def __init__(self, config_dir, extension="cfg"):
        # Save the path to the files
        if not os.path.isdir(config_dir):
            raise OSError(
                f"""Config directory is not a directory: {config_dir}""")
        self.config_dir: os.path.curdir = config_dir

        self.extension: str = extension

        # Load
        self.__load_config_files()

        # Verify
        for config in self.__dict__:
            if config.startswith("c_"):
                self.__validate_config_data(config)

    def __get_config_files(self) -> [os.path.abspath]:
        """
        :return: A list of absolute paths to the config files
        """
        return Path(self.config_dir).glob('*.' + self.extension)

    def __load_config_files(self):
        """
        For every file found by self.get_config_files,
        create an attribute with the name of the file without the extension,
        containing the parsed contents of the file.
        """
        for file_path in self.__get_config_files():
            name = str(file_path).rsplit('\\', maxsplit=1)[-1].removesuffix(
                '.' + self.extension)
            config = configparser.ConfigParser()
            config.read(file_path)
            setattr(self, 'c_'+name, config)

    def __validate_config_data(self, file):
        """This function validates configuration data using Regular
        Expressions (RegExp) to ensure that only valid data is parsed.
        It serves as a basic safeguard, although it does not guarantee
        that all parsed data is valid.
        However, it does help prevent some common mistakes."""
        validator = {
            "c_server": {
                "Server": {
                    "is_debug": REG_EXP_BOOLEAN,
                },
                "Database": {
                    "name": r"^.+\.db$",  # is "*.db"
                    "roles": REG_EXP_LIST
                },
                "Credentials.Submitted": {
                    "can_overlap_with_mail": REG_EXP_BOOLEAN
                }
            }
        }

        config: configparser.ConfigParser = self.get_config(file[2:])

        for section in config.sections():
            for option in config.options(section):
                # Get the data that needs to be verified.
                data = config.get(section, option)

                # Get the reg_exp to verify the data
                # if there is none continue to the next data.
                try:
                    reg_exp = validator[file][section][option]
                except KeyError:
                    continue

                # Verify
                m = re.match(pattern=reg_exp, string=data)
                # If the regexp did not find a match in the data,
                # raise an error.
                if m is None:
                    raise ValueError(
                        f"Option '{option}' in section '{section}' in {file[2:]}.cfg "
                        f"is not valid."
                    )

    def get(self, file, section, option) -> str:
        """
        :param file: The config file name, without the extension.
        :param section: The name of the section in the config file.
        :param option: The name of the option in the config file.
        :return: The value of the option under the given section
        in the given file.
        """
        return self.get_config(file)[section][option]

    def get_config(self, file):
        """
        :param file: The config file name, without the extension.
        :return: The config file parsed with configparser.ConfigParser()
        """
        return getattr(self, 'c_' + file)


tarot_config = Config(DEFAULT_CONFIG_DIR_PATH, extension="cfg")
