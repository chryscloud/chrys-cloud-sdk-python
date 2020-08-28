from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="chrysalis",
    version="1.0.0",
    author="Igor Rendulic",
    description="Chrysalis Python Cloud SDK for streaming live media",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chryscloud/chrys-cloud-sdk-python.git",
    packages=find_packages(),
    py_modules=['chrysalis'],
    keyword="rtmp video audio live stream camera surveillance",
    include_package_data=True,
    classifiers=[
        "Development Status :: 1.0.0",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache-License-2.0",
        "Operating System :: OS Independent",
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Conversion'
    ],
    install_requires=['redis', 'av', "numpy"],
    python_requires='>=3.6',
)