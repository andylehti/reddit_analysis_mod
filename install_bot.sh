#!/bin/bash

# Grab username from environment and directory from git clone
USERNAME=$(whoami)
DIRECTORY=$(pwd)

# Clone the GitHub repo
git clone https://github.com/andylehti/reddit_analysis_mod.git

# Change into the cloned directory
cd reddit_analysis_mod

# Update the DIRECTORY variable to the current directory
DIRECTORY=$(pwd)

# Install requirements
pip install -r requirements.txt

# Create service file with appropriate values
cat > reddit_bot.service <<EOF
[Unit]
Description=Reddit Bot Service
After=network.target

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=$DIRECTORY
ExecStart=/usr/bin/python3 reddit_bot.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Move the service file to the correct location and enable it
sudo mv reddit_bot.service /etc/systemd/system/reddit_bot.service
sudo systemctl enable reddit_bot
sudo systemctl start reddit_bot
