#!/bin/bash

/usr/bin/gunicorn -w 1 -b 0.0.0.0:9196 pushsafer_alertmanager_webhook:app
