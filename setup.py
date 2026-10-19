from setuptools import setup, find_packages

setup(
    name="tempmailc",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "async": ["httpx>=0.23.0"],
    },
)
