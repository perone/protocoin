from setuptools import setup
import protocoin

install_requirements = ['ecdsa>=0.10']

setup(
    name='protocoin',
    version=protocoin.__version__,
    url='https://github.com/perone/protocoin',
    license='BSD License',
    author=protocoin.__author__,
    author_email='christian.perone@gmail.com',
    description='A pure Python bitcoin protocol implementation.',
    long_description='A pure Python bitcoin protocol implementation.',
    install_requires=install_requirements,
    packages=['protocoin'],
    keywords='bitcoin, protocol',
    platforms='Any',
    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)