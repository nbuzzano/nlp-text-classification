from setuptools import setup, find_packages

setup(
    name="utils",
    version="1.0",
    author="nbuzzano",
    description="",
    long_description="",
    packages=["utils"],#packages=find_packages(),
    install_requires=[
        'scipy',
        'pandas',
        'sklearn',
        'nltk',
        'xgboost'
    ],
)