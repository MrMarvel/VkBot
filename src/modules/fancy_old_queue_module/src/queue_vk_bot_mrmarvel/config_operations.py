import configparser as cp
from . import gl_vars
from .gl_vars import CONFIG_FILENAME


def prepare_config() -> None:
    """
    Prepare config before loading.
    Adding default values instead of leak of them.
    :return:
    """

    config = cp.ConfigParser()
    config.read(CONFIG_FILENAME)

    api_label = 'API'
    if not config.has_section(api_label):
        config.add_section(api_label)
    api = config[api_label]
    if 'api_token' not in api:
        api['api_token'] = "6a9c267cd469388709a9e9acaddbe0aa81a0abbf12239b3e597a31729ffbddb9c88e80a443554c918b8f7"

    with open(CONFIG_FILENAME, 'w') as configfile:
        config.write(configfile)


def load_config() -> None:
    """
    Load main config
    :return:
    """

    prepare_config()
    config = cp.ConfigParser()
    config.read(CONFIG_FILENAME)
    gl_vars.token = config['API'].get('api_token')
