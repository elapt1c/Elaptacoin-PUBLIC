# Official ElaptaCoin PoW Miner
Welcome to the official page of ElaptaCoin Proof of Work Miner!

#### Here are features that the miner include:
1. **Auto-Reconnect** - If some expection occur or connection would be lost the miner would restart it self (The restarting could be interupted by pressing any key)

2. **Rust hasher** - For better hashing performance we decided to code the hasher inside the Rust

3. **One File** - Only one file `miner.py` needs to be executed. The rest gets installed afterwards
  e
5. **Auto Package Install** - The miner auto install all required packages

#### Platform support
1. Windows 10/11 (Theoretically Windows 7) **(Issues while exiting miner! Use Taskmgr!)**
2. Linux x32/x64
3. ARM x64 (AArch64)

#### Tech Support
Our discord server: https://discord.com/invite/4MzUF5s6xC

#### **Disclaimer! Keep in mind the miner is still in BETA, lot issues while exiting the miner can occur!**

# ElaptaCoin PoW Miner Setup Guide

## Windows
### 1. Download Python 3.8 or 3.9
We recomend downloading Python 3.8/3.9 from Microsoft Store, if you can't download Python 3.8/3.9 you can download it from Python offical webpage 

**_(Note that other versions of Python wouldn't work!)_**

### 2. Download the latest release of PoW ElaptaCoin
You can find the latest release on https://github.com/DuckyPolice/Elaptacoin-PUBLIC/releases/latest

### 3 Un-ZIP the latest release ZIP file

### 4. Open the Un-ZIPed directory in Powershell

### 5. (OPTIONAL) Create and Enter Python virtualenv
**>>>If you are having any issues with miner, try use virtualenv!<<<**

Virtualenv should be part of python, if you don't have it you can install the virtualenv by `pip3.9 install virtualenv` or `python3.8 -m venv venv`

Type `python3.9 -m venv venv` or `python3.8 -m venv venv` to create virtualenv

Then type `venv\Scripts\Activate.ps1` in order to activate virtualenv

Make sure there is `(.venv)` before path in powershell

### 6. Run the miner
To run the miner type `python miner.py` or `python3.9 miner.py` or `python3.8 miner.py`

And Enjoy! If experience some errors let us know on our discord server!

## Linux 64x/32x or Linux ARM x64
### 1. Download Python 3.8 or 3.9
We recomend downloading Python by pyenv

#### 1. Install pyenv
Type `curl https://pyenv.run | bash` to your linux console and wait till setup finishes

#### 2. Add pyenv to .bashrc
Type `sudo nano ~/.bashrc` go to end of the file and add these three lines: `export PATH="$HOME/.pyenv/bin:$PATH"` `eval "$(pyenv init --path)"` `eval "$(pyenv virtualenv-init -)"`

And save the file by pressing `CTRL+X`, press `Y` and then press `Enter`

Then type exec `$SHELL`

#### 3. Install the system packages
Type `sudo apt-get install --yes libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libgdbm-dev lzma lzma-dev tcl-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev wget curl make build-essential openssl`

Then confirm installation by pressing `Y` and wait till the installation finish

#### 4. Setup pyenv
Update the pyenv by typing `pyenv update`

And install the python by typing `pyenv install 3.9.13` or `pyenv install 3.8.10`

**_(Note that other versions of Python wouldn't work!)_**

### 2. Download the latest release of PoW ElaptaCoin
You can find the latest release on https://github.com/DuckyPolice/Elaptacoin-PUBLIC/releases/latest

### 3 Un-ZIP the latest release ZIP file
You can use `unzip` 

We recomend to place the directory with miner to user folder

### 4. Open the Un-ZIPed directory in bash

### 5. (OPTIONAL) Create and Enter Python virtualenv
**>>>If you are having any issues with miner, try use virtualenv!<<<**


Virtualenv should be part of python, if you don't have it you can install the virtualenv by `pip3.9 install virtualenv` or `python3.8 -m venv venv`

Type `python3.9 -m venv venv` or `python3.8 -m venv venv` to create virtualenv

Then type `source myvenv/bin/activate` in order to activate virtualenv

Make sure there is `(.venv)` before path in bash

### 6. Run the miner
**The miner needs to be executed by sudo privileges!**

To run the miner type `python miner.py` or `python3.9 miner.py` or `python3.8 miner.py`

And Enjoy! If experience some errors let us know on our discord server!

###### - Elaptacoin Team 2024, Written by tommarek