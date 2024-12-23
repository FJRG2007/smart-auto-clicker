<div align="center">
  <h1>Smart Auto Clicker</h1>
  <h3>Smart Auto Clicker - Automate your clicks easily.</h3>
  <img src="https://img.shields.io/badge/Python-purple?style=for-the-badge&logo=python&logoColor=white"/> 
  <a href="https://github.com/FJRG2007"> <img alt="GitHub" src="https://img.shields.io/badge/GitHub-purple?style=for-the-badge&logo=github&logoColor=white"/></a>
  <a href="https://ko-fi.com/fjrg2007"> <img alt="Kofi" src="https://img.shields.io/badge/Ko--fi-purple?style=for-the-badge&logo=ko-fi&logoColor=white"></a>
  <br />
  <hr />
</div>

<div align="center">
    <span>To use it, simply download the latest version.</span>
    <br />
    <img src="https://github.com/user-attachments/assets/df347e81-6030-470a-8c88-2532471357e9" />
</div>

### How to download and use

Check the releases [here](https://github.com/FJRG2007/smart-auto-clicker/tags).

### How to compile to an executable

1. Remember that you need to have Git and Python installed on your computer.

2. The first thing to do is to clone this repository.
```bash
git clone https://github.com/FJRG2007/smart-auto-clicker.git
```

3. Now enter the repository folder.
```bash
cd smart-auto-clicker
```

4. It is time to install the project dependencies.
```bash
pip install requirements.txt
```

5. Now it's time to compile the project.
```bash
pyinstaller --clean --onefile --noconsole --icon=assets/mouse.ico --add-data "assets;assets" --name="AutoClicker" init.py
```