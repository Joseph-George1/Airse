#!/bin/bash

# Check for Python 3
python3 --version >/dev/null 2>&1 || { echo "Looks like Python 3 decided to take a nap. Go wake it up! (Install required)"; exit 1; }

# Check for sudo privileges
sudo ls / >/dev/null 2>&1 || { echo "Uh oh, seems you don't have the key to the castle! (Sudo privileges needed)"; exit 1; }

# Check for aircrack-ng installation
aircrack-ng --version >/dev/null 2>&1 || { 
  echo "aircrack-ng is missing in action! We'll try to recruit it for your mission."
  sudo apt install aircrack-ng || { echo "Oh no, the recruitment failed! Maybe a manual installation is needed."; exit 1; }
  echo "aircrack-ng joined the party! Let's crack some protocoles ;)."
}

echo "All requirements are met. Prepare for takeoff!"
