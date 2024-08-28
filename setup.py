from setuptools import setup, find_packages

setup(
    name='janascard-qsource3',
    version='0.1.0',
    author='Juraj Jasik',
    author_email='juraj.jasik@gmail.com',
    description='Python library for controlling quadrupole mass filter RF generator QSource3 by Janascard.',
    packages=find_packages(),
    install_requires=[
        "scipy",
        "pymeasure"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
    ],
)