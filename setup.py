from setuptools import setup, find_packages

requires = [
    "flake8 >= 3.5.0",
]

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='flake8-rst',
    version='0.4.0',
    license="MIT",
    packages=find_packages(),
    url='https://github.com/kataev/flake8-rst',
    author='Denis Kataev',
    author_email='denis.a.kataev@gmail.com',
    install_requires=requires,
    description='flake8 for code in rst files and docstrings',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),

    entry_points={
        'console_scripts': [
            'flake8-rst = flake8_rst.cli:main'
        ]
    }
)
