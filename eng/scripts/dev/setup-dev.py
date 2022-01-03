import subprocess

INSTALL_VENV = "python -m pip install --user virtualenv"
SETUP_VENV = "python -m venv sprintern"


PIP_INSTALL = 'cd sprintern\Scripts && activate.bat && ' \
              'python -m pip install --upgrade pip &&' \
              'pip install wheel && ' \
              'pip install wheel && ' \
              'pip install azure-mgmt-compute && ' \
              'pip install azure-mgmt-network && ' \
              'pip install azure-eventhub && ' \
              'pip install azure-mgmt-containerservice && ' \
              'pip install azure-identity && ' \
              'pip install azure-keyvault'

subprocess.check_call(INSTALL_VENV, shell=True)
subprocess.check_call(SETUP_VENV, shell=True)
subprocess.check_call(PIP_INSTALL, shell=True)



