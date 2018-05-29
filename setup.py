from setuptools import setup,find_packages

setup(name='NMMSO',
      version='1.0',
      description='Python Implementation of the Niching Migratory Multi-Swarm Optimizer',
      author='Varchas Gopalaswamy',
      author_email='vgop@lle.rochester.edu',
      license='MIT',
      classifiers=[
            'Development Status :: 4 - Beta',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
        ],
      packages=find_packages(),
      download_url = 'https://github.com/varchasgopalaswamy/NMMSO/archive/1.0.tar.gz',
      keywords = ['optimizer','black','box','black-box','optimize','swarm','particle','niching','multi-modal'],
      install_requires=['numpy'],
      zip_safe=False)
