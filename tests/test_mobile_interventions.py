"""
Test interventions.py

11th May 2019
Written by Ed Oughton

"""
import pytest
from cdcam.interventions import decide_interventions, _area_satisfied
from cdcam.model import NetworkManager, PostcodeSector

@pytest.fixture
def basic_system(setup_lad, setup_pcd_sector, setup_assets,
    setup_capacity_lookup, setup_clutter_lookup,
    setup_simulation_parameters):

    system = NetworkManager(setup_lad, setup_pcd_sector,
        setup_assets, setup_capacity_lookup, setup_clutter_lookup,
        setup_simulation_parameters)

    return system


@pytest.fixture
def non_4g_system(setup_lad, setup_pcd_sector, setup_non_4g_assets,
    setup_capacity_lookup, setup_clutter_lookup,
    setup_simulation_parameters):

    system = NetworkManager(setup_lad, setup_pcd_sector,
        setup_non_4g_assets, setup_capacity_lookup,
        setup_clutter_lookup, setup_simulation_parameters)

    return system


@pytest.fixture
def mixed_system(setup_lad, setup_pcd_sector, setup_mixed_assets,
    setup_capacity_lookup, setup_clutter_lookup,
    setup_simulation_parameters):

    system = NetworkManager(setup_lad, setup_pcd_sector, setup_mixed_assets,
        setup_capacity_lookup, setup_clutter_lookup,
        setup_simulation_parameters)

    return system


@pytest.fixture
def empty_system(setup_lad, setup_pcd_sectors2, setup_non_4g_assets,
    setup_capacity_lookup_table2, setup_clutter_lookup,
    setup_simulation_parameters2):

    system = NetworkManager(setup_lad, setup_pcd_sectors2,
        setup_non_4g_assets, setup_capacity_lookup_table2, setup_clutter_lookup,
        setup_simulation_parameters2)

    return system


@pytest.fixture
def high_demand_system(setup_lad, setup_pcd_sectors2, setup_assets,
    setup_capacity_lookup_table2, setup_clutter_lookup,
    setup_simulation_parameters2):

    system = NetworkManager(setup_lad, setup_pcd_sectors2,
        setup_assets, setup_capacity_lookup_table2, setup_clutter_lookup,
        setup_simulation_parameters2)

    return system


def test_decide_interventions(non_4g_system, basic_system,
    mixed_system, empty_system, high_demand_system, setup_simulation_parameters,
    setup_simulation_parameters2):

    actual_result = decide_interventions(
        'minimal', 250000, 0,
        mixed_system, 2020, setup_simulation_parameters
    )

    assert actual_result == ([], 250000, [])

    actual_result = decide_interventions(
        'upgrade_to_lte', 331487, 2,
        non_4g_system, 2020, setup_simulation_parameters
    )

    assert len(actual_result[0]) == 2
    assert actual_result[1] == 0

    actual_result = decide_interventions(
        'upgrade_to_lte', 142446, 2,
        mixed_system, 2020, setup_simulation_parameters
    )

    assert actual_result == ([], 142446, [])

    actual_result = decide_interventions(
        'macrocell', (59210*2), 1000,
        mixed_system, 2020, setup_simulation_parameters
    )

    assert len(actual_result[0]) == 2
    assert actual_result[1] == 0

    actual_result = decide_interventions(
        'macrocell', 203668, 0,
        mixed_system, 2020, setup_simulation_parameters
    )

    assert len(actual_result[0]) == 0
    assert actual_result[1] == 203668

    actual_result = decide_interventions(
        'small-cell-and-spectrum', ((59210*2)+45882) , 1000,
        mixed_system, 2020, setup_simulation_parameters
    )

    assert len(actual_result[0]) == 3
    assert actual_result[1] == 0

    #test empty_system
    actual_result = decide_interventions(
        'small-cell-and-spectrum', 1e7 , 0,
        empty_system, 2020, setup_simulation_parameters2
    )

    macros_to_lte = len([a for a in actual_result[0] if  a['type'] == 'macrocell_site' \
                    and a['technology'] == 'LTE'])

    assert macros_to_lte == 4

    #test high_demand_system
    actual_result = decide_interventions(
        'small-cell-and-spectrum', 1e7 , 0,
        high_demand_system, 2020, setup_simulation_parameters2
    )

    macros_to_5g = len([a for a in actual_result[0] if  a['type'] == 'macrocell_site' \
                    and a['technology'] == '5G'])

    assert macros_to_5g == 4

    #test small cell build
    actual_result = decide_interventions(
        'small-cell-and-spectrum', 1e6 , 0,
        high_demand_system, 2020, setup_simulation_parameters2
    )

    small_cells = len([a for a in actual_result[0] if  a['type'] == 'small_cell'])

    assert small_cells == 4
