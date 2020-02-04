import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fogliodiagrammale",
    version="0.0.1",
    author="Giacomo Marchioro",
    author_email="giacomomarchioro@outlook.com",
    description="A tool for digitizing charts from drum hygrographs and thermo-hygrographs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/giacomomarchioro/fogliodiagrammale",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
