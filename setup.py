from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='python-moa',
    version='0.5.1',
    python_requires='>=3.6',
    description='Python Mathematics of Arrays (MOA)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Quansight-Labs/python-moa',
    keywords='tensor,compiler,moa',
    maintainer='Christopher Ostrouchov',
    maintainer_email='costrouchov@quansight.com',
    license='BSD 3-Clause License (Revised)',
    classifiers=[
        'Development Status :: 3 - Alpha',
        "License :: OSI Approved :: BSD License",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
    ],
    packages=find_packages(exclude=['docs', 'tests', 'notebooks', 'benchmarks']),
    install_requires=['astunparse'],
    extras_require={
        'moa': ['sly'],
        'viz': ['graphviz'],
        'test': ['sly', 'pytest', 'pytest-cov'],
        'docs': ['sphinx', 'sphinxcontrib-tikz'],
        'benchmark': ['numpy', 'numba']
    },
    project_urls={
        'Bug Reports': 'https://github.com/Quansight-Labs/python-moa/issues',
        'Source': 'https://github.com/Quansight-Labs/python-moa/sampleproject/',
        'Documentation': 'https://python-moa.readthedocs.io'
    },
)
