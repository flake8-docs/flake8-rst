Tuples are heterogenous, ordered collections.

Each element in a tuple is a value, and can be in multiple tuples and have multiple names (or no name)

.. code-block:: ipython

   In [8]: name = 'Brian'

   In [9]: other = brian

   In [10]: %timeit a = (1, 2,name)  # noqa: F821

   In [11]: b = (3, 4, other)

   In [12]: for i in range(3):
      ....:    print(a[i] is b[i])
      ....:

   Out[13]: False False True

.. nextslide:: Lists vs. Tuples

.. rst-class:: center large

    So Why Have Both?
