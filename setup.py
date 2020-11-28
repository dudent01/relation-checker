import pathlib
from distutils.core import setup
#from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name= "relation-checker",
    version= "0.1.0",
    description= "Semantic dynamic code analysis",
    long_description= README,
    long_description_content_type= "text/markdown",
    author= "Denis Rozhnov",
    author_email= "denis DOT a DOT rozhnov AT gmail DOT com",
    license= "",        # GNU GPLv3 or BSD
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing"
    ],
    packages= ["relation-checker"],
    include_package_data= True,
    install_requires= ["owlready2", "psutil"]
)