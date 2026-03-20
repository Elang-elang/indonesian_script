from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="indonesian_script",
    version="0.1.11a4",
    author="Elang muhammad",
    author_email="elangmahammad888@gmail.com",
    description="A programming language designed to make life easier for the Indonesian people",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/is",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "lark-parser>=0.12.0",
        "regex>=2026.1.15",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "is=indonesian_script.cli.main:main",
        ],
    },
    include_package_data=True
)
