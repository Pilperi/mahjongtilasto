import os
import datetime
import setuptools

# Jos suinkin mahdollista, lue versionumero versiofilusta.
# Muutoin päivämäärän mukaan.
VERSION = datetime.datetime.now().strftime("%Y.%m.%d.0")
VERSIOFILU = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "src", "mahjongtilasto", "VERSION"
)
if os.path.isfile(VERSIOFILU):
    with open(VERSIOFILU, "r") as fopen:
        VERSION = fopen.readline().rstrip()

setuptools.setup(
    name="mahjongtilasto",
    version=VERSION,
    url="https://github.com/Pilperi/mahjongtilasto",
    author="Pilperi",
    description="Yksinkertainen pistetilastojen hallinnointikirjasto",
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
    install_requires = [
		"PyQt5"
    ],
	python_requires=">=3.8, <4",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ]
)
