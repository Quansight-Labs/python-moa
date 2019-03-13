from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='python-moa',
    version='0.0.1',
    description='Python Mathematics of Arrays (MOA)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Quansight-Labs/python-moa',
    author='Christopher Ostrouchov',
    author_email='costrouchov@quansight.com',
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: BSD License",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='mathematics compiler moa',
    packages=find_packages(exclude=['docs', 'tests', 'notebooks']),
    python_requires='>=3.6',
    install_requires=['sly', 'astunparse'],
    extras_require={
        'viz': ['graphviz'],
        'test': ['pytest', 'pytest-cov'],
        'docs': ['sphinx', 'sphincontrib-tikz'],
    },
    project_urls={
        'Bug Reports': 'https://github.com/Quansight-Labs/python-moa/issues',
        'Source': 'https://github.com/Quansight-Labs/python-moa/sampleproject/',
        'Documentation': 'https://python-moa.readthedocs.io'
    },
)
