import setuptools

__version__ = "1.0.0"

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyeem",
    version=__version__,
    author="Drew Meyers",
    author_email="drewm@mit.edu",
    description="A description",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/drewmee/PyEEM",
    license="MIT",
    packages=setuptools.find_packages(exclude=["tests*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    test_suite="tests",
    install_requires=[
        "tensorly",
        "tensorflow==2.2.0",
        "keras",
        "numpy",
        "pandas",
        "h5py",
        "tables",
        "matplotlib==3.2.2",
        "seaborn",
        "celluloid",
        "urllib3",
        "boto3",
        "scipy==1.4.1",
    ],
)
