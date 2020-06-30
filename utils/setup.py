from setuptools import setup, find_packages

setup(
    name="utils",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "Flask==1.1.2",
        "pika==1.1.0",
        "mysql-connector==2.2.9"
    ],
)
