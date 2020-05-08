from setuptools import setup, find_packages

with open("README.md", encoding='utf-8') as fp:
    long_description = fp.read()

setup(
    name = "dictutils",
    version = "0.1",
    license="MIT",
    description = "A collection of useful tools for manipulating dictionaries.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = "Adi Eyal",
    author_email = "adi@openup.org.za",
    url = "https://github.com/adieyal/dictutils",
    download_url = "https://github.com/adieyal/dictutils/archive/v0.1.tar.gz",
    packages=find_packages(),
    keywords = ["dictionary", "utility"],
    #install_requires = [],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
