import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyControl4",  # Replace with your own username
    version="0.0.2",
    author="lawtancool",
    author_email="26829131+lawtancool@users.noreply.github.com",
    description="Python 3 asyncio package for interacting with Control4 systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lawtancool/pyControl4",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
