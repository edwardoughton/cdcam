===============
Getting Started
===============

In this document, we provide an introductory overview of the data, functions and results
for how to use ``cdcam`` with the example project.

To run and reproduce the example project, download the data from the Zonodo repository,
preprocess the data using scripts/preprocess.py, and then execute scripts/run.py to
generate the results.

The data available from the Zonodo repository contains a number of folders including:

- Mobile coverage information from Ofcom (ofcom_2018).
- Population growth scenarios for local authority districts (population_scenarios).
- Polygon shapes for postcode sectors and local authority districts (shapes).
- Sitefinder cell site location data (sitefinder).
- Capacity lookup table data by spectrum frequency (system_simulator).

Create a NetworkManager
-----------------------

The NetworkManager object imported from src/cdcam/model.py requires the following inputs:

- local authority districts
- postcode sectors
- assets
- capacity_lookup_table
- clutter_lookup
- simulation_parameters

A local authority district information (upper level statistical units) needs to contain
name and id fields as a list of dictionaries:

.. code-block:: python

    [
        {
            'name': 'Cambridge',
            'id': 'E07000008'
        }
    ]

Equally, the postcode sectors (lower level statistical units) must contain the
upper level lad id (lad_id), the area in kilometers square (area_km2),
postcode sectors id (id), average user data consumption (user_throughput), and
population for the timestep being modelled, as follows:

.. code-block:: python

    [
        {
            'lad_id': 'E07000008',
            'area_km2': 0.9965977842344768,
            'id': 'CB12',
            'user_throughput': 4.78,
            'population': 5287
        }
    ]

Existing cell site data is required, which is referred to here as the initial
system. Each cell site needs to contain the current cellular generation present
(technology) such as 4G, the type of cell site (type), the date the site was
built (build_date), the site id (site_ngr), the frequencies deployed (frequency)
and the postcode sector id which the site is within (pcd_sector):

.. code-block:: python

    {
        {
            'technology': 'LTE',
            'type': 'macrocell_site',
            'build_date': 2016,
            'site_ngr': 'site_27856',
            'frequency': ['800', '1800', '2600'],
            'pcd_sector': 'L33'
        }
    }

The capacity lookup table needs to be loaded as follows:

.. code-block:: python

    {
        ('urban', 'macro', '3700', '40', '5G'): [
            (0.11276372445109878, 5.101430894167686),
            (0.20046884346862007, 21.097341086638664),
            (0.4510548978043951, 79.9233194517426),
            (1.8042195912175805, 319.6932778071853)
        ]
    }

The clutter lookup table details the population densities which represent
different urban, suburban or rural environments, as follows:

.. code-block:: python

    [
        (0.0, 'rural'),
        (782.0, 'suburban'),
        (7959.0, 'urban')
    ]

A dictionary of simulation parameters is required containing annual budget, market share,
any frequency bandwidths and ot

.. code-block:: python

    {
        'annual_budget': 600000000.0,
        'market_share': 0.3,
        'channel_bandwidth_700': '10'
    }

And then create a NetworkManager called system:

.. code-block:: python

    system = NetworkManager(lads, pcd_sectors, assets, capacity_lookup_table,
                            clutter_lookup, simulation_parameters)


Decide interventions
--------------------

Once the NetworkManager has been created, the decide_interventions function can then be
imported and used from src/cdcam/interventions.py

The decide_interventions function requires the following intputs:

- strategy
- budget
- service_obligation_capacity
- system
- timestep
- simulation_parameters

The strategy is a string such as:

.. code-block:: python

    'small-cell'

and the budget is an integer such as:

.. code-block:: python

    500000000

The service obligation is dependent on whether one is specified. If not just use zero:

.. code-block:: python

    0

The NetworkManager object created earlier can then be passed as the system.

The timestep can be passed as an interger as follows:

.. code-block:: python

    2020

And a dictionary of simulation parameters can also be passed:

.. code-block:: python

    {
        'annual_budget': 600000000.0,
        'market_share': 0.3,
        'channel_bandwidth_700': '10'
    }

For each time period, the decide_interventions function will return three items including:

- a list of built interventions
- the remaining budget
- the amount of capital spent

The list of built interventions for the small cell strategy will look as follows:

.. code-block:: python

    [
        {
            'bandwidth': ['50', '200'],
            'pcd_sector': 'DN215',
            'type': 'small_cell',
            'technology': '5G',
            'build_date': 2027,
            'population_density': 52.41802733317741,
            'lad_id': 'E07000142', 'site_ngr':
            'small_cell_site',
            'frequency': ['3700', '26000']
        }
    ]


Results
-------

To obtain results, we can then add the newly built interventions to the existing assets:

    assets += interventions_built

And then create an updated NetworkManager which includes new assets:

    system = NetworkManager(lads, pcd_sectors, assets, capacity_lookup_table,
                            clutter_lookup, simulation_parameters)

New results can then be obtained by calling methods belonging to each LAD or
PostocdeSector object:

.. code-block:: python

    for lad_id, lad in system.lads.values():
        print(lad_id, lad.capacity)

Might result in:

.. code-block:: python

    E07000012 96.92010607478302
    E07000008 134.0466728466086
