from setuptools import setup, find_packages
import os

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='graccsum',
      version='4.2.0',
      description='GRACC Summary Agent',
      author_email='dweitzel@cse.unl.edu',
      author='Derek Weitzel',
      url='https://opensciencegrid.github.io/gracc',
      package_dir={'': 'src'},
      packages=['graccsum'],
      install_requires=requirements,
      entry_points= {
            'console_scripts': [
                  'graccsumperiodic = graccsum.periodic_summarizer:main',
                  'graccsummarizer = graccsum.summarize:main'
            ]
      }
)
