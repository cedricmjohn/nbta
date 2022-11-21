from setuptools import find_packages
from setuptools import setup

with open('requirements.txt') as f:
    content = f.readlines()
requirements = [x.strip() for x in content if 'git+' not in x]

setup(name='nbta',
      version="0.2.2",
      description="nbta is the Notebook Teaching Assistant helping with meaningful feedback and error management for Python",
      packages=find_packages(),
      install_requires=requirements,
      url='https://github.com/cedricmjohn/nbta',
      author='Cedric John',
      author_email='cedric.john@gmail.com',
      test_suite='tests',
      # include_package_data: to install data from MANIFEST.in
      include_package_data=True,
      scripts=['scripts/nbta-run'],
      zip_safe=False)
