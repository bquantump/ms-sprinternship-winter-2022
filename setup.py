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
        #'--upgrade pip',
        'wheel',
        'azure-mgmt-compute',
        'azure-mgmt-network',
        'azure-eventhub',
        'azure-mgmt-containerservice',
        'azure-identity',
        'azure-keyvault',
        'azure-keyvault-secrets',
    ],
    packages=['deployer'],
    include_package_data=True,
    entry_points={
        'console_scripts': ['grcdeployer=deployer.deployer:deployer']
    }
)