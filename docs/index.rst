.. dictutils documentation master file

Welcome to dictutils
====================

Small, dependency-free utilities for nested dictionaries: merge, pivot, aggregate, reshape.

**See it in action**

Transform flat data into nested aggregations with ``nest_agg``:

.. code-block:: python

   from dictutils.nestagg import nest_agg, Agg

   # Sales data
   sales = [
       {"region": "US", "product": "laptop", "revenue": 1200, "units": 1},
       {"region": "US", "product": "laptop", "revenue": 1200, "units": 1}, 
       {"region": "US", "product": "phone", "revenue": 800, "units": 1},
       {"region": "EU", "product": "laptop", "revenue": 1100, "units": 1},
       {"region": "EU", "product": "phone", "revenue": 750, "units": 1},
   ]

   # Group by region → product with revenue totals and averages
   result = nest_agg(sales, keys=["region", "product"], aggs={
       "total_revenue": Agg(map=lambda x: x["revenue"], zero=0),
       "avg_revenue": Agg(
           map=lambda x: (x["revenue"], 1),
           zero=(0, 0), 
           reduce=lambda a, b: (a[0] + b[0], a[1] + b[1]),
           finalize=lambda x: x[0] / x[1]
       ),
       "units_sold": Agg(map=lambda x: x["units"], zero=0)
   })

   # Result:
   # {
   #   "US": {
   #     "laptop": {"total_revenue": 2400, "avg_revenue": 1200.0, "units_sold": 2},
   #     "phone": {"total_revenue": 800, "avg_revenue": 800.0, "units_sold": 1}
   #   },
   #   "EU": {
   #     "laptop": {"total_revenue": 1100, "avg_revenue": 1100.0, "units_sold": 1}, 
   #     "phone": {"total_revenue": 750, "avg_revenue": 750.0, "units_sold": 1}
   #   }
   # }

**Quick links**

- :doc:`quickstart` - Get started in 5 minutes
- :doc:`core` - Core functions (qsdict, mergedict, pivot, nestagg)
- :doc:`ops` - Advanced operations (20+ utilities)
- :doc:`cookbook` - Real-world examples
- :doc:`api_reference` - Complete API documentation

**External links**

- `GitHub Repository <https://github.com/adieyal/dictutils>`_
- `PyPI Package <https://pypi.org/project/dictutils/>`_
- `Issue Tracker <https://github.com/adieyal/dictutils/issues>`_

Contents
--------

.. toctree::
   :maxdepth: 2

   quickstart
   core
   ops
   cookbook
   api_reference

