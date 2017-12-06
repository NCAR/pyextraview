from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='extraview',
    version='0.0.1',
    description='API to query Extraview',
    long_description=readme,
    author='Nathan Rini',
    author_email='nate@ucar.edu',
    url='https://github.com/nateucar/pyextraview',
    license=license,
    packages=find_packages('extraview'),
)
