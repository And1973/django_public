from setuptools import setup

setup(name='viesapi',
      version='1.2.6',
      description='VIES API Client for Python',
      url='https://viesapi.eu',
      author='NETCAT',
      author_email='firma@netcat.pl',
      license='https://www.apache.org/licenses/LICENSE-2.0',
      packages=['viesapi'],
      zip_safe=False,
      install_requires=['lxml', 'python-dateutil'])
