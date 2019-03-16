from setuptools import find_packages, setup

setup(
    name='perimeterator',
    version='0.1.0',  # TODO: Single source this from bagger.version.VERSION
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
    scripts=[],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
    install_requires=[
        'boto3==1.9.108'
    ]
)