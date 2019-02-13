from setuptools import find_packages, setup, Command

setup(
    name='perimeterator',
    version='0.1.0',  # TODO: Single source this from bagger.version.VERSION
    description='Continuous AWS Perimeter Monitoring',
    author='Peter Adkins',
    author_email='peter.adkins@kernelpicnic.net',
    url='https://www.github.com/darkarnium/bagger',
    packages=find_packages('src'),
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    package_dir={
        'bagger': 'src/bagger',
    },
    scripts=[
        'src/baggercli'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
    install_requires=[
        'click==6.6',
        'PyYAML==3.12',
        'cerberus==1.2',
        'adns @ git+https://github.com/trolldbois/python3-adns.git@master',
    ]
)
