.. ipython:: python
   :suppress:
   import os
   import sys

   sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum.

.. ipython:: python
    import matplotlib.pyplot as plt

    @savefig plot_simple.png width=4in
    plt.plot([1, 2, 3, 4]); plt.ylabel('some numbers');

Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum.

.. ipython:: python
    import numpy as np

    @savefig hist_simple.png width=4in
    hist(np.random.randn(10000), 100)
