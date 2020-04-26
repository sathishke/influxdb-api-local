import os
import logging.config

import yaml


default_path='./config/logging.yaml'
default_level=logging.INFO
env_key='LOG_CFG'

"""Setup logging configuration

"""
path = default_path
value = os.getenv(env_key, None)
if value:
    path = value
if os.path.exists(path):
    with open(path, 'rt') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

else:
    logging.basicConfig(level=default_level, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')