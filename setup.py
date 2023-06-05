from setuptools import find_packages, setup

setup(
    name="forecast",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "matplotlib==3.7.1",
        "numpy==1.24.3",
    ],
)
