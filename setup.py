from setuptools import setup, find_packages
import os

def read_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read the contents of your README file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="lisu-framework-ontology",
    version="0.1.0",
    author="MDOF Team",
    author_email="your.email@example.com",  # Replace with your email
    description="LISU Framework Ontology UI - A VR visualization and control interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/MDOF-Ontology",  # Replace with your repo URL
    packages=find_packages(exclude=['tests*']),
    install_requires=read_requirements(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        'lisu_framework': ['resources/*'],
    },
    entry_points={
        'console_scripts': [
            'lisu-ontology=lisu_framework.run_ui:main',
        ],
    },
) 