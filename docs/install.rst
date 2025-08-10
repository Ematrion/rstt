.. _install:

==================
Installation guide
==================

Python versions
===============

RSTT requires python 3.10 +


Installation
============

You can install RSTT from PyPi with::

    pip install rstt


Dependencies
------------

RSTT relies on the following python packages:

* `names`_ to provides random name for players.
* `typeguard`_ for runtime type-check.
* `numpy`_ as a computing tool.


Integration
-----------

RSTT was develloped with intent to be used alongside other packages to test.
You can integrate in your simulation rating system like:

* `trueskill`_, a famous rating system in video game.
* `openskill`_, a revent alternative.


Develloper
----------

RSTT is open source and welcomes any contribution. Once you have read the `guidlines`_ you can start working.

1. Get the code
.. code-block:: bash

    git clone https://github.com/Ematrion/rstt.git

    cd rstt

2. Install Dependencies with Poetry

The project is build using `poetry`_.  If you also use it then simply:

.. code-block:: bash

    poetry install --with dev

3. Alternative Installation

If you do use poetry you need to perform manually steps, 

    1. Create a virtual environement
   
    .. code-block:: bash

        python -m venv .venv
    
    2. activate it

    On macOS/Linux

    .. code-block:: bash

        source .venv/bin/activate
    
    On Windows

    .. code-block:: bash
        
        .venv\Scripts\activate

    3. Install Dependencies
    
    .. code-block:: bash

        pip install --editable '.[dev]'

4. Check your Installation

Make sure everything works fine and run the tests with::
    pytest








.. _names: https://pypi.org/project/names/
.. _typeguard: https://typeguard.readthedocs.io/en/latest/
.. _numpy: https://numpy.org
.. _trueskill: https://trueskill.org
.. _openskill: https://openskill.me/en/stable/

.. _guidlines: https://github.com/Ematrion/rstt/blob/main/CONTRIBUTING.md
.. _poetry: https://python-poetry.org