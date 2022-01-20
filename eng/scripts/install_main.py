import subprocess
import sys

branch = sys.argv[1] if len(sys.argv) > 1 else 'dev'

clone = 'git clone https://github.com/microsoft/azure-software-radio.git'
cd = f'cd azure-software-radio/gr-azure-software-radio; git checkout {branch};' \
     'pip3 install -r python/requirements.txt; mkdir build; cd build; cmake ..; sudo make install -j'

subprocess.check_call(clone, shell=True)
subprocess.check_call(cd, shell=True)

clone_hack = 'git clone https://github.com/bquantump/hackathon2021.git; cd hackathon2021/dsp; pip3 install -e . '
subprocess.check_call(clone_hack, shell=True)
install_oot_hack = 'cd hackathon2021/gr-eventhubs; git checkout demo; mkdir build; cd build; cmake ..; sudo make install -j'
subprocess.check_call(install_oot_hack, shell=True)