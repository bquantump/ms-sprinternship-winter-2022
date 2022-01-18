import subprocess

clone = 'git clone https://github.com/microsoft/azure-software-radio.git'
cd = 'cd azure-software-radio/gr-azure-software-radio; git checkout dev;' \
     'pip3 install -r python/requirements.txt; mkdir build; cd build; cmake ..; sudo make install -j'

subprocess.check_call(clone, shell=True)
subprocess.check_call(cd, shell=True)