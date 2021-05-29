from pathlib import Path
from setuptools import setup
from setuptools import find_packages

requirements = Path("requirements.txt").read_text().split("\n")
readme = Path("README.md").read_text()

setup(
    name='gimp-console',
    version='0.2.0',
    packages=find_packages(),
    url='https://github.com/isman7/gimp-python-development/',
    license='GNU GPLv3',
    author='ibenito',
    author_email='ismaelbenito@protonmail.com',
    description='A GTK Python Console for the GIMP python environment',
    install_requires=requirements,
    package_data={"gimp.plugins.console": ["console"]},
    long_description=readme,
    long_description_content_type='text/markdown',
)
