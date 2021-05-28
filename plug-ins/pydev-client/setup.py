from pathlib import Path
from setuptools import setup
from setuptools import find_packages

requirements = Path("requirements.txt").read_text().split("\n")

setup(
    name='gimp-pydev-pycharm',
    version='0.1.0',
    packages=find_packages(),
    url='https://github.com/isman7/gimp-python-development/',
    license='GNU GPLv3',
    author='ibenito',
    author_email='ismaelbenito@protonmail.com',
    description='A PyDev for PyCharm debugging inside the GIMP python environment',
    install_requires=requirements,
    package_data={"gimp.plugins.pydev": ["pydev"]}
)
