Installation steps
==================


..

    Installation steps
    ==================

    .. _installation_step:

    Installing Python distribution (Anaconda)
    -----------------------------------------

    Anaconda is a famous python data science platform.
    It is distributed with scientific libraries such as pandas, scipy, numpy, matplotlib, etc. and
    IDE such as jupiter or spyder. One can find more information about anaconda distribution on : https://www.anaconda.com/distribution/

    For a fast, ready to use python platform follow the link : http://www.gurobi.com/downloads/get-anaconda
    and follow the steps.

        - Step one: Download and install Anaconda
        - Step two: Install Gurobi into Anaconda

        .. code-block:: none

            conda config --add channels http://conda.anaconda.org/gurobi
            conda install gurobi

        - Step three : install a Gurobi Licence on http://www.gurobi.com/downloads/licenses/license-center

        This step requires you to login and ask for a free university licence or free commercial evaluation licence depending on your status.
        Store this licence in ``C:/gurobiXXX/`` for instance and create an environment variable named ``GUROBI_LICENCE`` pointing to ``C:/gurobiXXX/gurobi.lic``.


    Install Gurobi Solver
    ---------------------

    If you already have a python distribution and/or do not want to install all the anaconda distribution, you can install Gurobi software.
    In the installation file, one will also find the python package gurobipy. Install it using ``python setup install``.

    Install Gurobi see :
        - http://www.gurobi.com/index
        - http://www.gurobi.com/documentation/7.5/quickstart_mac/the_gurobi_python_interfac.html

        .. note:: Installation file of Gurobi should be added to the environment variable ``PATH``, so python can find the solver.
            Note that the version of gurobi (32 or 64 bits) must match with your python installation.

    Install a Gurobi Licence on http://www.gurobi.com/downloads/licenses/license-center
    This step requires you to login and ask for a free university licence or free commercial evaluation licence depending on your status.
    Store this licence in ``C:/gurobiXXX/`` for instance and create an environment variable named ``GUROBI_LICENCE`` pointing to ``C:/gurobiXXX/gurobi.lic``.


    Install LLMSE from source
    -------------------------

    Clone the repository and install the package using the ``setup.py`` file.

        .. code-block:: bash

            git clone https://github.com/ReinboldV/llmse.git <PATH>
            python setup.py install

        .. note:: This command require GIT to be installed on your system. One can install it from : https://git-scm.com/downloads.
            Otherwise, you may download the library in a zip format here : https://github.com/ReinboldV/llmse/archive/gh-pages.zip.

    Install dependencies
    --------------------

    LLMES also has conditional dependencies on a variety of third-party Python packages.
    These are not installed with ``llmse``, and many of them can be installed using ``pip``.

        .. code-block:: none

            pip install gurobipy
            pip install numpy
            pip install matplotlib
            pip install pandas
            pip install sphinx

        For sphinx documentation, note that LLMES uses some extensions that should also be installed. See ``\docs\conf.py`` for the complete list.

        .. literalinclude:: conf.py
            :lines: 34-40