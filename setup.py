from setuptools import setup, find_packages
import os


setup(name='graccsum',
      version='1.2',
      description='GRACC Summary Agent',
      author_email='dweitzel@cse.unl.edu',
      author='Derek Weitzel',
      url='https://opensciencegrid.github.io/gracc',
      package_dir={'': 'src'},
      packages=['graccsum'],
      install_requires=['elasticsearch',
      'pika',
      'six',
      'toml',
      'urllib3',
      'wsgiref'
      ],
      entry_points= {
            'console_scripts': [
                  'graccsumperiodic = graccsum.periodic_summarizer:main',
                  'graccsummarizer = graccsum.summarize:main'
            ]
      }
)
