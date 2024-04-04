import subprocess
import shlex

def check_and_install_requirements():
  """Checks for Python 3, sudo privileges, and aircrack-ng suite installation.
  Attempts to install missing requirements using 'sudo apt install'

  Returns:
      True if all requirements are met, False otherwise.
  """

  # Check for Python 3 using subprocess
  try:
    subprocess.run(["python3", "--version"], check=True, capture_output=True)
  except subprocess.CalledProcessError:
    print("Looks like Python 3 decided to take a nap. Go wake it up! (Install required)")
    return False

  # Check for sudo privileges
  try:
    subprocess.run(["sudo", "ls", "/"], check=True, capture_output=True)
  except subprocess.CalledProcessError:
    print("Uh oh, seems you don't have the key to the castle! (Sudo privileges needed)")
    return False

  # Check for aircrack-ng installation
  try:
    subprocess.run(["aircrack-ng", "--version"], check=True, capture_output=True)
  except subprocess.CalledProcessError:
    print("aircrack-ng is missing in action! We'll try to recruit it for your mission.")
    try:
      install_command = shlex.split("sudo apt install aircrack-ng")
      subprocess.run(install_command, check=True)
      print("aircrack-ng joined the party! Let's crack some protocoles ;).")
    except subprocess.CalledProcessError:
      print("Oh no, the recruitment failed! Maybe a manual installation is needed.")
      return False

  print("All requirements are met. Prepare for takeoff!")
  return True

if __name__ == "__main__":
  check_and_install_requirements()
