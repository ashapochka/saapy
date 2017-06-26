[![Build Status](https://travis-ci.org/ashapochka/saapy.svg?branch=master)](https://travis-ci.org/ashapochka/saapy)

# SAApy - System Architecture Assessment Toolkit

The assessment toolkit provides a set of tools implemented in python helping
build a graph from software system artifacts such as source code structures,
dependencies, issues, commit history, and others, and analyze the software
system for its quality and technical debt based on this graph.

The framework is a research tool and is not of stable production quality yet.

* [Documentation](docs/index.md)
* [IDempiere Assessment Demo](samples/idempiere-assessment.ipynb)

## Installation Steps

To setup saapy based environment please follow steps similar to below.
The saapy library is not on pypi yet hence a somewhat unconventional process.

1. Make sure you have python 3.5+ installed and use it as a default python
environment in the next steps.
2. Create the projects root directory:
    ```bash
    mkdir ~/Projects && cd ~/Projects
    ```
3. Clone saapy from GitHub. If you have it already cloned, you can skip this step.
    ```bash
    git clone https://github.com/ashapochka/saapy.git
    ```
4. Create python3 virtual environment to isolate saapy specific installation.
    ```bash
    pyvenv saapyenv
    ```
5. Activate the environment and run further steps in it (check on terminal cmd prefix)
    ```bash
    source saapyenv/bin/activate
    ```
6. Install *numpy* explicitly otherwise *pymc* installation fails later on.
    ```bash
    pip install numpy
    ```
7. Install saapy third party dependencies in a batch (can take a couple of minutes).
    ```bash
    pip install -r saapy/requirements.txt
    ```
8. Install saapy itself in the development mode.
    ```bash
    pip install -e ./saapy
    ```

## Assessment Environment

First, make sure you executed the steps in the Installation section. To prepare
the assessment environment for a specific project follow the steps:

1. Create a project working directory.
    ```bash
    mkdir ~/Projects/prj1 && cd ~/Projects/prj1
    ```
2. Activate the environment if inactive.
    ```bash
    source ../saapyenv/bin/activate
    ```
3. Add any files required for processing into the working directory.
4. Run Jupyter notebook server to write and execute assessment notebooks
based on the saapy.
    ```bash
    jupyter-notebook --working-dir=`pwd`
    ```


(c) Andriy Shapochka
