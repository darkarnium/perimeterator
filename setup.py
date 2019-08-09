import os
from setuptools import find_packages, setup

# Source the version from the package.
__version__ = 'Unknown'
exec(open('src/perimeterator/version.py').read())

setup(
    name='perimeterator',
    version=__version__,
    description='Continuous AWS Perimeter Monitoring',
    author='Peter Adkins',
    author_email='peter.adkins@kernelpicnic.net',
    url='https://www.github.com/darkarnium/perimeterator',
    packages=find_packages('src'),
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    package_dir={
        'perimeterator': 'src/perimeterator',
    },
    scripts=[
        'src/enumerator.py',
        'src/scanner.py',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
    install_requires=[
        'boto3==1.9.204'
    ]
)
