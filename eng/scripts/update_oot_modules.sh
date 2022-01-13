git clone https://github.com/microsoft/azure-software-radio.git
cd azure-software-radio/gr-azure-software-radio
git checkout d3c9ea2
mkdir build; cd build; cmake ..
sudo make install -j

