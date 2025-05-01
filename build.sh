#!/usr/bin/env bash

playwright install chromium

# Download chromedriver compatible with the installed Chromium version
wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip -P /tmp
unzip /tmp/chromedriver_linux64.zip -d /tmp
mv /tmp/chromedriver /usr/local/bin/
