How to build the documentation ?
================================


One can build the documentation using the ``make`` command in ``\docs``.

	.. code-block:: none

		cd docs\
		make html

or, for a pdf documentation,

	.. code-block:: none

		cd docs\
		make latex
		cd build\latex
		pdflatex lms2.tex Documentation.pdf
