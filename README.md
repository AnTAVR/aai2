Arch AnTAVR Installer
===

Arch Linux installer for beginners
http://archlinux.org.ru/forum/topic/10992/

git clone https://github.com/AnTAVR/aai2.git

cd aai2

git submodule init

git submodule update

python3 -m venv venv

python3 -m venv --upgrade venv

./get_text.sh

source venv/bin/activate

pip install pytest

pip install pythondialog

#easy_install pythondialog

cd src

pytest

python -m unittest discover

./main.py
