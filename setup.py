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
    packages=['lms2', 'lms2.core', 'lms2.base', 'lms2.environment',
              'lms2.fluids',
              'lms2.logical',
              'lms2.mechanic',
              'lms2.social',
              'lms2.template',
              'lms2.thermal',
              'lms2.electric'],
    classifiers=["Programming Language :: Python :: 3.6"],
)
