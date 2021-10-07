Installation steps
*******************

.. _installation_step:

Installing Python distribution (Anaconda)
==========================================

Anaconda is a famous python data science platform.
It is distributed with scientific libraries such as pandas, scipy, numpy, matplotlib, etc. and
IDE such as jupiter or spyder. One can find more information about anaconda distribution on : https://www.anaconda.com/distribution/

lms2 is a library based on the pyomo package (https://github.com/Pyomo/pyomo). Pyomo is a Python-based open-source software package that supports a diverse set of optimization capabilities for formulating and analyzing optimization models. Pyomo can be used to define symbolic problems, create concrete problem instances, and solve these instances with standard solvers.


    1. Download and install Anaconda
    2. Create a new conda environment from environment.yml
        .. code-block:: none

            conda env create -f environment.yml

    3. (optional) Example for installing other packages you may need (solvers, data-processing, etc.).

        .. code-block:: none

            conda install -c conda-forge pyomo
            conda config --add channels http://conda.anaconda.org/gurobi
            conda install gurobi
            conda install -c conda-forge glpk

   4. (optional) Install a Gurobi Licence on http://www.gurobi.com/downloads/licenses/license-center

    This step requires you to login and ask for a licence depending on your status (free for universities and for evaluation).
    Store this licence in ``C:/gurobiXXX/`` for instance and create an environment variable named ``GUROBI_LICENCE`` pointing to ``C:/gurobiXXX/gurobi.lic``.


Install LMS2 from source
========================

Clone the repository and install the package using the ``setup.py`` file.

    .. code-block:: bash

        git clone https://github.com/ReinboldV/lms2.git lms2
        pip install -e ./lms2

    .. note:: This command require GIT to be installed on your system. One can install it from : https://git-scm.com/downloads.
