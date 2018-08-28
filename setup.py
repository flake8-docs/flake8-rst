from setuptools import setup, find_packages

requires = [
    "flake8 >= 3.5.0",
]

setup(
    name='flake8-rst',
    version='0.2',
    license="MIT",
    packages=find_packages(),
    url='https://github.com/kataev/flake8-rst',
    author='Denis Kataev',
    author_email='denis.a.kataev@gmail.com',
    install_requires=requires,
    description='flake8 for code in rst files and docstrings',
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),

    entry_points={
        'console_scripts': [
            'flake8-rst = flake8_rst.cli:main'
        ]
    }
)
