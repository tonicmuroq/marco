# coding: utf-8

import sys

from marco.app import create_app, DEV_MODE

app = create_app()

if __name__ == '__main__':
    port = 5000
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    app.run('0.0.0.0', port, debug=DEV_MODE)
