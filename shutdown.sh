#!/bin/bash

sudo ufw delete allow 5000
sudo ufw status numbered

echo "Server shutdown successfully."
