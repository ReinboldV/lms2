from setuptools import setup
import versioneer

commands = versioneer.get_cmdclass().copy()

setup(
    name='lms2',
    version=versioneer.get_version(),
    description='Library for Linear Modelling of Energetic Systems',
    author='Vincent Reinbold',
    author_email='vincent.reinbold@gmail.com',
    license='BSD',
    packages=['lms2',
              'lms2.core',
              'lms2.base',
              'lms2.electric'],
    install_requires=['matplotlib', 'numpy', 'pandas', 'pyomo', 'scipy', 'networkx'],
    classifiers=["Programming Language :: Python :: 3.6"],
)
