from setuptools import setup

setup(
    name='grcdeployer',
    version="0.1",
    description='Deployer for compute functions',
    long_description="",
    license='MIT',
    author='Microsoft Corporation',
    url='https://github.com/bquantump/ms-sprinternship-winter-2022',
    zip_safe=False,
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=[
        'pyyaml',
        'wheel',
        'azure-mgmt-resource',
        'azure-mgmt-keyvault',
        'azure-mgmt-compute',
        'azure-mgmt-network',
        'azure-eventhub',
        'azure-mgmt-containerservice',
        'azure-identity',
        'azure-keyvault',
        'azure-keyvault-secrets',
        'azure-mgmt-eventhub',
        'azure-mgmt-storage'
    ],
    packages=['deployer'],
    package_data={'':['install_main.py']},
    data_files=[('eng/scripts',['eng/scripts/install_main.py'])],
    include_package_data=True,
    entry_points={
        'console_scripts': ['grcdeployer=deployer.deployer:deployer']
    }
)