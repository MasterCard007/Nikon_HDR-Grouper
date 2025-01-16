from setuptools import setup, find_packages

setup(
    name="HDR-Grouper",
    version="1.0.0",
    description="A Python tool to organize HDR photo sets by grouping NEF files based on EXIF metadata.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="",
    url="https://github.com/yourusername/HDR-Grouper",
    packages=find_packages(),
    py_modules=["HDR_Grouper_v10"],
    install_requires=[
        "exifread",
        "tqdm",
        "icecream"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "hdr-grouper=HDR_Grouper_v10:main",
        ],
    },
)
