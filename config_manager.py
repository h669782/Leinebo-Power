# config_manager.py
import configparser

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config
