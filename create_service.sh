#!/bin/bash

# Validate arguments
if [[ $# -ne 2 ]] ; then
    echo 'Usage: ./create_service.sh <username> </path/to/your/script/directory>'
    exit 1
fi

# Assign arguments to variables
USERNAME=$1
DIRECTORY=$2

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
