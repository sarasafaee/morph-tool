# setup.py
from setuptools import setup, find_packages

setup(
    name='morph-tool',
    version='0.1.0',
    description='A Qt-based GUI for morphological analogy and report generation',
    author='Your Name',
    packages=find_packages(where='.'),
    package_dir={'': '.'},
    include_package_data=True,
    install_requires=[
        'PyQt5',
        'matplotlib',
        'Jinja2',
        'reportlab',
    ],
    entry_points={
        'console_scripts': [
            # After installation, users can just run `morph-tool`
            'morph-tool = run_app:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
