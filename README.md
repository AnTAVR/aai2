Arch AnTAVR Installer
===

Arch Linux installer for beginners
http://archlinux.org.ru/forum/topic/10992/

git clone https://github.com/AnTAVR/aai2.git
git submodule init
git submodule update

python3 -m venv env
python3 -m venv --upgrade env

./get_text.sh

cd src
source ../env/bin/activate

pip install pytest
pip install pytest-smartcov
pip install pytest-sugar

pip install pythondialog
#easy_install pythondialog

source ../env/bin/activate
pytest
python -m unittest discover
