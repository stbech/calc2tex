import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = "0.0.4"
PACKAGE_NAME = "calc2tex"
AUTHOR = "Stefan Becherer"
AUTHOR_EMAIL = "becherer.stefan1@gmail.com"
URL = "https://github.com/stbech/calc2tex"

LICENSE = "MIT License"
DESCRIPTION = "Calculating formulas and displaying them in LaTeX"
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
    "numpy",
    #"pint"
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      package_data={
          "": ["*.txt"]
          },
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages()
      )