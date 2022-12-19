import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="CADET-Python",
    version="0.14",
    author="William Heymann",
    author_email="w.heymann@fz-juelich.de",
    description="CADET is a python interface to the CADET chromatography simulator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/modsim/CADET-Python",
    packages=setuptools.find_packages(),
    install_requires=[
          'addict',
          'numpy',
          'h5py <= 3.6.0',
          'filelock'
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
) 
