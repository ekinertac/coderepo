from setuptools import setup, find_packages

setup(
    name='coderepo',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'coderepo=coderepo.coderepo:main',
        ],
    },
    install_requires=[],
    python_requires='>=3.6',
    url='https://github.com/ekinertac/coderepo',
    license='MIT',
    author='Ekin Ertaç',
    author_email='ekinertac@gmail.com',
    description='A tool to collect code files into structured formats.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    test_suite='tests',
)
