# coding: utf-8

import os
import yaml
from macro.app import create_app


def load_config():
    with open('config.yaml', 'r') as f:
        os.environ.update(yaml.load(f))


load_config()
app = create_app()

if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)
