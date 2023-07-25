#!/bin/bash

echo "This will reboot at the end, cancel now if you do not wish this to happen."

# Install necessary system packages
sudo apt-get update && sudo apt-get -y upgrade
sudo apt-get install -y python3-pip python3-dev python3.10-venv cron
sudo apt-get install -y libsm6 libxext6 libxrender-dev
sudo apt-get install -y nodejs npm
sudo apt-get install -y tesseract-ocr libtesseract-dev

# Install packages with pip
pip3 install nltk transformers vaderSentiment fuzzywuzzy pytesseract python-Levenshtein python-dotenv

# Add Python user bin to PATH
echo "export PATH=$PATH:/home/$USER/.local/bin" >> ~/.bashrc
source ~/.bashrc

# Clone the repository and navigate into it
git clone https://github.com/andylehti/reddit_analysis_mod
cd reddit_analysis_mod

# Create a Python virtual environment and activate it
python3.10 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install the Python packages
pip install praw easyocr nltk

# Install the requirements from the provided file
pip install -r requirements.txt

# Reboot the system
sudo reboot
