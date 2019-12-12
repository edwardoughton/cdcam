"""This script is a self-contained example of running cdcam to simulate a small system.
"""
from copy import copy

# The NetworkManager represents the whole system under simulation
from cdcam.model import NetworkManager
# decide_interventions uses simple rules to decide what to build
from cdcam.interventions import decide_interventions

# A local authority district (upper level statistical unit) needs to contain name and id
# fields, and be part of a list of dictionaries
lads = [
    {
        "id": 'E07000008',
        "name": "Cambridge",
    }
]

# Equally, each postcode sector (lower level statistical unit) must contain the upper level lad
# id (lad_id), the area in kilometers square (area_km2), postcode sector id (id), average user
# data consumption (user_throughput), and population for the timestep being modelled, as
# follows:
pcd_sectors = [
    {
        "id": "CB11",
        "lad_id": 'E07000008',
        "population": 5000,
        "area_km2": 2,
        "user_throughput": 2,
    },
    {
        "id": "CB12",
        "lad_id": 'E07000008',
        "population": 20000,
        "area_km2": 2,
        "user_throughput": 2,
    }
]

# Existing cell site data is required, which is referred to here as the initial system. Each
# cell site needs to contain the current cellular generation present (technology) such as 4G,
# the type of cell site (type), the date the site was built (build_date), the site id
# (site_ngr), the frequencies deployed (frequency) and the postcode sector id which the site is
# within (pcd_sector):
initial_system =  [
    {
        "pcd_sector": "CB11",
        "site_ngr": "site_100",
        "technology": "",
        "type": "macrocell_site",
        "frequency": [],
        "bandwidth": "",
        "build_date": 2012,
        "sectors": 3,
        'opex': 10000,
    },
    {
        "pcd_sector": "CB12",
        "site_ngr": "site_200",
        "technology": "",
        "type": "macrocell_site",
        "frequency": [],
        "bandwidth": "",
        "build_date": 2012,
        "sectors": 3,
        'opex': 10000,
    }
]

# The capacity lookup table needs to be loaded as follows (see details in the
# cdcam.model.NetworkManager API documentation).
capacity_lookup_table = {
    # Keys are tuples of:
    # (area,   asset,   frequency, bandwidth, technology generation)
    ('urban', 'macro', '800',     '10',     '4G'): [
        # Values are lists of tuples of:
        # (asset density, mean cell edge capacity at that density)
        (0.01,            1),
        (0.1,             10),
        (1,               100),
        (2,               200)
    ],
    ('urban', 'macro', '2600', '10', '4G'): [
        (0.01, 1), (0.1, 10), (1, 100), (2, 200)
    ],
    ('urban', 'macro', '700', '10', '5G'): [
        (0.01, 1), (0.1, 10), (1, 100), (2, 200)
    ],
    ('urban', 'macro', '3500', '40', '5G'): [
        (0.01, 1), (0.1, 10), (1, 100), (2, 200)
    ],
    ('urban', 'macro', '26000', '200', '5G'): [
        (0.01, 1), (0.1, 10), (1, 100), (2, 200)
    ],
    ('urban', 'micro', '800', '10', '4G'): [
        (0.01, 1), (0.1, 10), (1, 100), (2, 200)
    ],
    ('urban', 'micro', '2600', '10', '4G'): [
        (0.01, 1), (0.1, 10), (1, 100), (2, 200)
    ],
    ('urban', 'micro', '3700', '40', '5G'): [
        (0.01, 1), (0.1, 10), (1, 100), (2, 200)
    ],
    ('urban', 'micro', '26000', '200', '5G'): [
        (0.01, 1), (0.1, 10), (1, 100), (2, 200)
    ],
    ('urban', 'micro', '26000', '200', '5G'): [
        (0.01, 1), (0.1, 10), (1, 100), (2, 200)
    ],
}

# The clutter lookup table details the population densities which represent different urban,
# suburban or rural environments:
clutter_lookup = [
    (0.0, 'rural'), (782.0, 'suburban'), (7959.0, 'urban')
]

# A dictionary of simulation parameters is required containing annual budget, market share,
# any frequency bandwidths:
simulation_parameters = {
    'market_share': 0.3,
    'annual_budget': 1e6,
    'service_obligation_capacity': 10,
    'busy_hour_traffic_percentage': 20,
    'coverage_threshold': 100,
    'penetration': 80,
    'channel_bandwidth_700': '10',
    'channel_bandwidth_800': '10',
    'channel_bandwidth_1800': '10',
    'channel_bandwidth_2600': '10',
    'channel_bandwidth_3500': '40',
    'channel_bandwidth_3700': '40',
    'channel_bandwidth_26000': '200',
    'macro_sectors': 3,
    'small-cell_sectors': 1,
    'mast_height': 30,
}

# For a scenario analysis, we would provide multiple future population projections. At a
# minimum, each area needs some value for population.
population_by_scenario_year_pcd = {
    'baseline':{
        2020: {
            'CB11': 100000,
            'CB12': 200000,
        },
        2021: {
            'CB11': 110000,
            'CB12': 220000,
        },
        2022: {
            'CB11': 121000,
            'CB12': 232000,
        },
    }
}

# For a scenario analysis, we would also provide multiple data demand (user data throughput)
# projections. At a minimum, each area needs some value for per-user throughput.
user_throughput_by_scenario_year = {
    'baseline': {
        2020: 1,
        2021: 2,
        2022: 3,
    }
}

# Setting up a short simulation run
BASE_YEAR = 2020
END_YEAR = 2022
TIMESTEP_INCREMENT = 1
TIMESTEPS = range(BASE_YEAR, END_YEAR + 1, TIMESTEP_INCREMENT)

# Scenario combinations to test. Population and throughput scenarios are defined above.
# Interventions strategies are defined in src/cdcam/interventions.py as
# AVAILABLE_STRATEGY_INTERVENTIONS and include 'minimal', 'upgrade_to_lte', 'macrocell' and
# 'small-cell'
scenario_combinations = [
    # population, throughput, interventions strategy
    ('baseline', 'baseline', 'small-cell-and-spectrum'),
]


for pop_scenario, throughput_scenario, intervention_strategy in scenario_combinations:
    print(' ')
    print("Running:", pop_scenario, throughput_scenario, intervention_strategy)

    assets = copy(initial_system)

    for year in TIMESTEPS:
        print(' ')
        print('----------------------------------------------------')
        print("-", year, "(", pop_scenario, throughput_scenario, intervention_strategy, ")")
        print('----------------------------------------------------')
        print(' ')

        for pcd_sector in pcd_sectors:
            pcd_sector_id = pcd_sector["id"]
            pcd_sector["population"] = (
                population_by_scenario_year_pcd[pop_scenario][year][pcd_sector_id])
            pcd_sector["user_throughput"] = (
                user_throughput_by_scenario_year[throughput_scenario][year])

        budget = simulation_parameters['annual_budget']
        service_obligation_capacity = simulation_parameters['service_obligation_capacity']

        if year == BASE_YEAR:
            # Run initial simulation
            system = NetworkManager(
                lads,
                pcd_sectors,
                assets,
                capacity_lookup_table,
                clutter_lookup,
                simulation_parameters)

        # Decide what to build this year
        interventions_built, budget, spend = decide_interventions(
            intervention_strategy,
            budget,
            service_obligation_capacity,
            system,
            year,
            simulation_parameters)

        # Add new assets to existing system assets
        assets += interventions_built

        # Run simulation with built assets
        system = NetworkManager(
            lads,
            pcd_sectors,
            assets,
            capacity_lookup_table,
            clutter_lookup,
            simulation_parameters)

        # Report on assets built
        print(' ')
        print('Built {} new assets in {}:'.format(len(interventions_built), year))

        print('-- {} LTE Macro Cells'.format(
            len([
                a for a in interventions_built
                if  a['type'] == 'macrocell_site' and a['technology'] == 'LTE'])))

        print('-- {} 5G Macro Cells'.format(
            len([
                a for a in interventions_built
                if a['type'] == 'macrocell_site' and a['technology'] == '5G'])))

        print('-- {} 5G Small Cells'.format(
            len([
                a for a in interventions_built if a['type'] == 'small_cell'])))

        # Report summary financials
        print(' ')
        print('Financials')
        print('----------')

        print('£££ - Spent £{} million'.format(
            round((simulation_parameters['annual_budget'] - budget) / 1e6, 1)))

        print('£££ - Budget remaining £{} million'.format(
            round(budget / 1e6, 1)))

        # Report details of demand and capacity
        # Per Local Authority District (larger area)
        print(' ')
        for lad in system.lads.values():
            print('{}:'.format(lad.name))
            print('-- Demand (Mbps/km²): {},'.format(round(lad.demand())))
            print('-- Capacity (Mbps/km²): {}'.format(round(lad.capacity())))

        # Per postcode sector (smaller area)
        print(' ')
        for pcd in system.postcode_sectors.values():
            print('{}:'.format(pcd.id))
            print('-- Demand (Mbps/km²): {},'.format(round(pcd.demand)))
            print('-- Capacity (Mbps/km²): {}'.format(round(pcd.capacity)))
        print(' ')
