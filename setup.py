import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "JFJDigitizer",
    version = "0.0.4",
    author = "Jamal Makkor",
    author_email = "makkor@uni-bremen.de",
    description = ("Software to digitize JFJ spectra."),
    license = "GNU",
    keywords = "Spectra",
    url = "",
    packages=[
        "autoflake==1.3.1",
        "backcall==0.1.0",
        "contourpy==1.0.6",
        "cycler==0.10.0",
        "decorator==4.4.2",
        "dtwalign==0.1.0",
        "fonttools==4.38.0",
        "image-slicer==2.1.1",
        "ipython==7.14.0",
        "ipython-genutils==0.2.0",
        "jedi==0.17.0",
        "joblib==0.15.1",
        "kiwisolver==1.2.0",
        "llvmlite==0.33.0",
        "matplotlib==3.2.1",
        "networkx==2.4",
        "numba==0.50.1",
        "numpy==1.18.4",
        "opencv-python==4.2.0.34",
        "packaging==23.0",
        "pandas==1.0.5",
        "parso==0.7.0",
        "pexpect==4.8.0",
        "pickleshare==0.7.5",
        "Pillow==7.1.2",
        "prompt-toolkit==3.0.5",
        "ptyprocess==0.6.0",
        "pyflakes==2.2.0",
        "Pygments==2.6.1",
        "pyparsing==2.4.7",
        "pysolar==0.9",
        "python-dateutil==2.8.1",
        "pyttk==0.3.2",
        "pytz==2020.1",
        "scikit-learn==0.23.1",
        "scipy==1.4.1",
        "seaborn==0.10.1",
        "six==1.15.0",
        "sklearn==0.0.post1",
        "threadpoolctl==2.1.0",
        "tk==0.1.0",
        "traitlets==4.3.3",
        "wcwidth==0.1.9",
    ],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: GNU License",
    ],
)