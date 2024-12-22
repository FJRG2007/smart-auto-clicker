# Smart Auto Clicker

To use it, simply download the latest version.

Check the releases [here](https://github.com/FJRG2007/smart-auto-clicker/tags).

### How to compile to an executable

1. If you do not have the `pyinstaller` package installed, now is the time to install it.
```bash
pip install pyinstaller
```

2. Now it's time to compile the project.
```bash
pyinstaller --clean --onefile --noconsole --icon=assets/mouse.ico --name="AutoClicker" main.py
```