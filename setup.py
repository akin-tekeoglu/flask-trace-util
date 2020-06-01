"""
Setup module
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask-trace-util",
    version="0.0.6",
    author="Akın Tekeoğlu",
    author_email="akin.tekeoglu@gmail.com",
    description="Trace utility for flask",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akin-tekeoglu/flask-trace-util",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=["Flask", "requests"],
)
