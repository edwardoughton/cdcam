from cdcam.model import NetworkManager
from cdcam.interventions import decide_interventions

lads = [
        {
            "id": 'E07000008',
            "name": "Cambridge",
        }
    ]

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

clutter_lookup = [
    (0.0, 'rural'), (782.0, 'suburban'), (7959.0, 'urban')
]

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
    }
}

user_throughput_by_scenario_year = {
    'baseline': {
        2020: 1,
        2021: 2
    }
}

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

capacity_lookup_table = {
    ('urban', 'macro', '800', '10', '4G'): [
        (0.01, 1), (0.1, 10), (1, 100), (2, 200)
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

if __name__ == '__main__':

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

    BASE_YEAR = 2020
    END_YEAR = 2022
    TIMESTEP_INCREMENT = 1
    TIMESTEPS = range(BASE_YEAR, END_YEAR + 1, TIMESTEP_INCREMENT)

    for pop_scenario, throughput_scenario, intervention_strategy in [

        ('baseline', 'baseline', 'small-cell-and-spectrum'),

        ]:
        print("Running:", pop_scenario, throughput_scenario, intervention_strategy)

        assets = initial_system[:]

        for year in TIMESTEPS:
            print('---------------------------------------------')
            print(' ')
            print("-", year)
            print(' ')

            for pcd_sector in pcd_sectors:
                try:
                    pcd_sector_id = pcd_sector["id"]
                    pcd_sector["population"] = (
                        population_by_scenario_year_pcd \
                            [pop_scenario][year][pcd_sector_id])
                    pcd_sector["user_throughput"] = (
                        user_throughput_by_scenario_year \
                            [throughput_scenario][year])
                except:
                    pass

            budget = simulation_parameters['annual_budget']
            service_obligation_capacity = simulation_parameters['service_obligation_capacity']

            if year == BASE_YEAR:
                system = NetworkManager(lads, pcd_sectors, assets,
                    capacity_lookup_table, clutter_lookup,
                    simulation_parameters)

            interventions_built, budget, spend = decide_interventions(
                intervention_strategy, budget, service_obligation_capacity,
                system, year, simulation_parameters)

            print(' ')
            print('Built {} new assets in {}:'.format(len(spend), year))

            print('-- {} LTE Macro Cells'.format(
                len([a for a in interventions_built if  a['type'] == 'macrocell_site' \
                    and a['technology'] == 'LTE'])))

            print('-- {} 5G Macro Cells'.format(
                len([a for a in interventions_built if  a['type'] == 'macrocell_site' \
                    and a['technology'] == '5G'])))

            print('-- {} 5G Small Cells'.format(
                len([a for a in interventions_built if a['technology'] == 'small_cell'])))

            print(' ')

            #Add new assets to existing system assets
            assets += interventions_built

            system = NetworkManager(lads, pcd_sectors, assets,
                capacity_lookup_table, clutter_lookup,
                simulation_parameters)

            print(' ')
            print('**Financials**')
            print('£££ - Spent £{} million'.format(round((simulation_parameters['annual_budget'] - budget) / 1e6, 1)))
            print('£££ - Budget remaining £{} million'.format(round(budget / 1e6, 1)))
            print(' ')

            for lad in system.lads.values():
                print('{}:'.format(lad.name))
                print(' ')
                print('-- Demand (Mbps km^2): {},'.format(round(lad.demand())))
                print('-- Capacity (Mbps km^2): {}'.format(round(lad.capacity())))
