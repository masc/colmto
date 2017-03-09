"""
Optimisation of 2+1 Manoeuvres

Copyright 2017, Malte Aschermann.
Licensed under LGPL.
"""
import sys

from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ["tests"]
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


version = "0.1"

setup(name="optom",
      version=version,
      description="Optimisation of 2+1 Manoeuvres",
      long_description=open("README.md").read(),
      classifiers=[  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Programming Language :: Python"
      ],
      keywords="",  # Separate with spaces
      author="Malte Aschermann",
      author_email="masc@tu-clausthal.de",
      url="",
      license="LGPL",
      packages=find_packages(exclude=["examples", "tests", "sumo"]),
      include_package_data=True,
      zip_safe=False,
      tests_require=["pytest"],
      cmdclass={"test": PyTest},

      # TODO: List of packages that this one depends upon:
      install_requires=[
          "nose",
          "matplotlib",
          "sh",
          "lxml",
          "h5py",
          "PyYAML",
          "python-cjson",
          "progressbar",
          "doxypy"
      ],

      # TODO: List executable scripts, provided by the package (this is just an example)
      entry_points={
        "console_scripts":
        ["optom=run"]
      }
)
