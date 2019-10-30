===============
Getting Started
===============

This section walks through how to use ``cdcam`` with an example project.

The data folder available from the Zonodo repository contains a number of folders including:

- Mobile coverage information from Ofcom (ofcom_2018).
- Population growth scenarios for local authority districts (population_scenarios).
- Polygon shapes for postcode sectors and local authrotiy districts (shapes).
- Sitefinder cell site location data (sitefinder).
- Lookup table data (system_simulator).

===============
Create a NetworkManager
===============

The NetworkManager object imported from src/cdcam/model.py requires the following:

.. csv-table::
   :header:  "#", "Section", "Notes"
   :widths: 3, 10, 45

   1, Stepper, "Displays the status of the Modelrun job"
   2, Modelrun Configuation, "Provides an overview of the Modelrun configuration"
   3, Controls, "Provides run settings and a start/stop button for the Modelrun job"
   4, Console Output, "Real-time output from the Job runner process"


- local authority districts
- postcode sectors
- assets
- capacity_lookup_table
- clutter_lookup
- simulation_parameters

A list of dictionaries containing local authority districts is required, as so:

    [{'name': 'Cambridge', 'id': 'E07000008'}]

And a list of dictionaries containing lower spatial units, such as postcode sectors:

    [{'lad_id': 'E07000008', 'area_km2': 0.9965977842344768, 'id': 'CB12',
    'user_throughput': 4.78, 'population': 5287}]

The initial system needs to be loaded as:

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

    ('urban', 'macro', '3700', '40', '5G'): [
        (0.11276372445109878, 5.101430894167686),
        (0.20046884346862007, 21.097341086638664),
        (0.4510548978043951, 79.9233194517426),
        (1.8042195912175805, 319.6932778071853)
    ]

The clutter lookup table details the population densities which represent
different urban, suburban or rural environments, as follows:

    [
        (0.0, 'rural'),
        (782.0, 'suburban'),
        (7959.0, 'urban')
    ]

A dictionary of simulation parameters is required containing annual budget, market share,
any frequency bandwidths and ot

    {
        'annual_budget': 600000000.0,
        'market_share': 0.3,
        'channel_bandwidth_700': '10'
    }

===============
Decide interventions
===============

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

    'small-cell'

and the budget is an integer such as:

    500000000

The service obligation is dependent on whether one is specified. If not just use zero:

    0

The NetworkManager object can then be passed as the system:

    <cdcam.model.NetworkManager object at 0x0000016A10CAD278>

The timestep can be passed as an interger as follows:

    2020

And a dictionary of simulation parameters can also be passed:

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

===============
Results
===============

To obtain results, we can then add the newly built interventions to the existing assets:

    assets += interventions_built

And then create an updated NetworkManager which includes new assets:

    system = NetworkManager(lads, pcd_sectors, assets, capacity_lookup_table,
                            clutter_lookup, simulation_parameters)

New results can then be obtained by calling methods belonging to each LAD or
PostocdeSector object:

    for lad in system.lads.values():
        print(lad.capacity)

Results in:

    96.92010607478302
    134.0466728466086
