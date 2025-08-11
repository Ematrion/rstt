.. _install:

===========================
Installation Guide
===========================

Python Versions
===============
RSTT requires Python 3.10+.

Installation
============

You can install RSTT from PyPI with:


.. code-block:: bash

    pip install rstt

Dependencies
------------

RSTT relies on the following Python packages:

* `names`_ — provides random names for players.

* `typeguard`_ — for runtime type-checking.

* `numpy`_ — as a computing tool.

Integration
-----------

RSTT was developed with the intent to be used alongside other packages for testing. You can integrate it into your simulation rating system like:

* `trueskill`_, a famous rating system in video games.

* `openskill`_, a recent alternative.

Developer
---------

RSTT is open source and welcomes contributions. Once you have read the `guidelines`_, you can start working.

1. Get the code:
   
   
   ::

       git clone https://github.com/Ematrion/rstt.git

   
   and then:
   
   
   ::
       
       cd rstt

2. Install Dependencies with Poetry

   The project is built using `poetry`_. If you also use it, simply run:
   
   
   ::
       
       poetry install --with dev

3. Alternative Installation

   If you don’t use Poetry, you need to perform the steps manually:

   a. Create a virtual environment:
   
       
       ::
              
              python -m venv .venv

   b. Activate it:

      - On macOS/Linux:
  
       
       ::
              
              source .venv/bin/activate

      - On Windows:

       
       ::
              
              .venv\Scripts\activate

   c. Install dependencies:
   
       
       ::
              
              pip install --editable '.[dev]'

4. Check Your Installation

   Make sure everything works fine by running the tests with::

       pytest

.. _names: https://pypi.org/project/names/
.. _typeguard: https://typeguard.readthedocs.io/en/latest/
.. _numpy: https://numpy.org
.. _trueskill: https://trueskill.org
.. _openskill: https://openskill.me/en/stable/

.. _guidelines: https://github.com/Ematrion/rstt/blob/main/CONTRIBUTING.md
.. _poetry: https://python-poetry.org
