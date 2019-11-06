import os
import sys
import configparser
import csv
import fiona
import time

from shapely.geometry import shape, Point, LineString, mapping
from shapely.ops import  cascaded_union
from tqdm import tqdm

from rtree import index

from collections import OrderedDict

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

#####################################
# setup file locations and data files
#####################################

DATA_RAW = os.path.join(BASE_PATH)
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')

#####################################
# READ MAIN DATA
#####################################

def read_lads():
    """
    Read in all lad shapes.

    """
    lad_shapes = os.path.join(
        DATA_RAW, 'shapes', 'lad_uk_2016-12.shp'
        )

    with fiona.open(lad_shapes, 'r') as lad_shape:
        return [lad for lad in lad_shape if
            not lad['properties']['name'].startswith((
                'E06000053',
                'S12000027',
                'N09000001',
                'N09000002',
                'N09000003',
                'N09000004',
                'N09000005',
                'N09000006',
                'N09000007',
                'N09000008',
                'N09000009',
                'N09000010',
                'N09000011',
                ))]


def lad_lut(lads):
    """
    Yield lad IDs for use as a lookup.

    """
    for lad in lads:
        yield lad['properties']['name']


def read_postcode_sectors(path):
    """
    Read all postcode sector shapes.

    """
    with fiona.open(path, 'r') as pcd_sector_shapes:
        return [pcd for pcd in pcd_sector_shapes]


def add_lad_to_postcode_sector(postcode_sectors, lads):
    """
    Add the LAD indicator(s) to the relevant postcode sector.

    """
    final_postcode_sectors = []

    idx = index.Index(
        (i, shape(lad['geometry']).bounds, lad)
        for i, lad in enumerate(lads)
    )

    for postcode_sector in tqdm(postcode_sectors):
        for n in idx.intersection(
            (shape(postcode_sector['geometry']).bounds), objects=True):
            postcode_sector_centroid = shape(postcode_sector['geometry']).centroid
            postcode_sector_shape = shape(postcode_sector['geometry'])
            lad_shape = shape(n.object['geometry'])
            if postcode_sector_centroid.intersects(lad_shape):
                final_postcode_sectors.append({
                    'type': postcode_sector['type'],
                    'geometry': postcode_sector['geometry'],
                    'properties':{
                        'id': postcode_sector['properties']['RMSect'],
                        'StrSect': postcode_sector['properties']['StrSect'],
                        'lad': n.object['properties']['name'],
                        'area': postcode_sector_shape.area,
                        },
                    })
                break

    return final_postcode_sectors


def write_arc_shapes(postcode_sectors, filename, directory):

    data = []

    LAD_AREAS = [
        'E06000031',
        'E07000005',
        'E07000006',
        'E07000007',
        'E06000032',
        'E06000042',
        'E06000055',
        'E06000056',
        'E07000004',
        'E07000008',
        'E07000009',
        'E07000010',
        'E07000011',
        'E07000012',
        'E07000150',
        'E07000151',
        'E07000152',
        'E07000153',
        'E07000154',
        'E07000155',
        'E07000156',
        'E07000177',
        'E07000178',
        'E07000179',
        'E07000180',
        'E07000181',
    ]

    for postcode_sector in postcode_sectors:
        if postcode_sector['properties']['lad'] in LAD_AREAS:
            data.append({
                'type': postcode_sector['type'],
                'geometry': postcode_sector['geometry'],
                'properties': {
                    'id': postcode_sector['properties']['id'],
                    'lad': postcode_sector['properties']['lad'],
                    'StrSect': postcode_sector['properties']['StrSect'],
                    'area': postcode_sector['properties']['area'],
                }
            })

    prop_schema = []
    for name, value in data[0]['properties'].items():
        fiona_prop_type = next((
            fiona_type for fiona_type, python_type in \
                fiona.FIELD_TYPES_MAP.items() if \
                python_type == type(value)), None
            )

        prop_schema.append((name, fiona_prop_type))

    sink_driver = 'ESRI Shapefile'
    sink_crs = {'init': 'epsg:27700'}
    sink_schema = {
        'geometry': data[0]['geometry']['type'],
        'properties': OrderedDict(prop_schema)
    }

    if not os.path.exists(directory):
        os.makedirs(directory)

    with fiona.open(
        os.path.join(directory, filename), 'w',
        driver=sink_driver, crs=sink_crs, schema=sink_schema) as sink:
        for datum in data:
            sink.write(datum)

    return print('complete')


def load_coverage_data(lad_id):
    """
    Import Ofcom Connected Nations coverage data (2018).

    """
    path = os.path.join(
        DATA_RAW, 'ofcom_2018', '201809_mobile_laua_r02.csv'
        )

    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for line in reader:
            if line['laua'] == lad_id:
                return {
                    'lad_id': line['laua'],
                    'lad_name': line['laua_name'],
                    '4G_geo_out_0': line['4G_geo_out_0'],
                    '4G_geo_out_1': line['4G_geo_out_1'],
                    '4G_geo_out_2': line['4G_geo_out_2'],
                    '4G_geo_out_3': line['4G_geo_out_3'],
                    '4G_geo_out_4': line['4G_geo_out_4'],
                }

def load_in_weights():
    """
    Load in postcode sector domestic delivery addresses to use as
    population weights.

    """
    path = os.path.join(
        DATA_RAW, 'intermediate', 'population_weights.csv'
        )

    population_data = []

    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for line in reader:
            population_data.append({
                'id': line['postcode_sector'],
                'population': int(line['domestic_delivery_points']),
            })

    return population_data


def add_weights_to_postcode_sector(postcode_sectors, weights):
    """
    Add weights to postcode sector

    """
    output = []

    for postcode_sector in postcode_sectors:
        pcd_id = postcode_sector['properties']['id'].replace(' ', '')
        for weight in weights:
            weight_id = weight['id'].replace(' ', '')
            if pcd_id == weight_id:
                output.append({
                    'type': postcode_sector['type'],
                    'geometry': postcode_sector['geometry'],
                    'properties': {
                        'id': pcd_id,
                        'lad': postcode_sector['properties']['lad'],
                        'population_weight': weight['population'],
                        'area_km2': (postcode_sector['properties']['area'] / 1e6),
                    }
                })

    return output


def calculate_lad_population(postcode_sectors):
    """
    Get lad population by aggregating from postcode sectors.

    """
    lad_ids = set()

    for pcd_sector in postcode_sectors:
        lad_ids.add(pcd_sector['properties']['lad'])

    lad_population = []

    for lad_id in lad_ids:
        population = 0
        for pcd_sector in postcode_sectors:
            if pcd_sector['properties']['lad'] == lad_id:
                population += pcd_sector['properties']['population_weight']
        lad_population.append({
            'lad': lad_id,
            'population': population,
        })

    output = []

    for pcd_sector in postcode_sectors:
        for lad in lad_population:
            if pcd_sector['properties']['lad'] == lad['lad']:

                weight = (
                    pcd_sector['properties']['population_weight'] /
                    lad['population']
                )

                output.append({
                    'type': pcd_sector['type'],
                    'geometry': pcd_sector['geometry'],
                    'properties': {
                        'id': pcd_sector['properties']['id'],
                        'lad': pcd_sector['properties']['lad'],
                        'population': lad['population'] * weight,
                        'weight': weight,
                        'area_km2': pcd_sector['properties']['area_km2'],
                        'pop_density_km2': (
                            weight /
                            (pcd_sector['properties']['area_km2'] / 1e6)
                            ),
                    },
                })

    return output


def get_forecast(filename):
    """
    Load existing population forecasts by lad.

    """
    folder = os.path.join(DATA_RAW, 'population_scenarios')

    with open(os.path.join(folder, filename), 'r') as source:
        reader = csv.DictReader(source)
        for line in reader:
            yield {
                'year': line['timestep'],
                'lad': line['lad_uk_2016'],
                'population': line['population'],
            }


def disaggregate(forecast, postcode_sectors):
    """
    Dissaggregate lad population to postcode sector level.

    """
    output = []

    # seen_lads = set()

    for line in forecast:
        forecast_lad_id = line['lad']
        for postcode_sector in postcode_sectors:
            pcd_sector_lad_id = postcode_sector['properties']['lad']
            if forecast_lad_id == pcd_sector_lad_id:
                output.append({
                    'year': line['year'],
                    'lad': line['lad'],
                    'id': postcode_sector['properties']['id'],
                    'population': int(
                        float(line['population']) *
                        float(postcode_sector['properties']['weight'])
                        )
                })

    return output


def generate_scenario_variants(postcode_sectors, directory):
        """
        Function to disaggregate LAD forecasts to postcode level.

        """
        print('Checking total GB population')
        population = 0
        for postcode_sector in postcode_sectors:
            population += postcode_sector['properties']['population']
        print('Total GB population is {}'.format(population))

        files = [
            'arc_population__baseline.csv',
            'arc_population__0-unplanned.csv',
            'arc_population__1-new-cities-from-dwellings.csv',
            'arc_population__2-expansion.csv',
            'arc_population__3-new-cities23-from-dwellings.csv',
            'arc_population__4-expansion23.csv',
        ]

        print('loaded luts')
        for scenario_file in files:

            print('running {}'.format(scenario_file))
            forecast = get_forecast(scenario_file)

            disaggregated_forecast = disaggregate(forecast, postcode_sectors)

            filename = os.path.join('pcd_' + scenario_file)

            print('writing {}'.format(filename))
            csv_writer(disaggregated_forecast, directory, filename)


def allocate_4G_coverage(postcode_sectors, lad_lut):

    output = []

    for lad_id in lad_lut:

        sectors_in_lad = get_postcode_sectors_in_lad(postcode_sectors, lad_id)

        total_area = sum([s['properties']['area_km2'] for s in \
            get_postcode_sectors_in_lad(postcode_sectors, lad_id)])

        coverage_data = load_coverage_data(lad_id)

        coverage_amount = float(coverage_data['4G_geo_out_4'])

        covered_area = total_area * (coverage_amount/100)

        ranked_postcode_sectors = sorted(
            sectors_in_lad, key=lambda x: x['properties']['pop_density_km2'], reverse=True
            )

        area_allocated = 0

        for sector in ranked_postcode_sectors:

            area = sector['properties']['area_km2']
            total = area + area_allocated

            if total < covered_area:

                sector['properties']['lte'] = 1
                output.append(sector)
                area_allocated += area

            else:

                sector['properties']['lte'] = 0
                output.append(sector)

                continue

    return output


def get_postcode_sectors_in_lad(postcode_sectors, lad_id):

    for postcode_sector in postcode_sectors:
        if postcode_sector['properties']['lad'] == lad_id:
            if isinstance(postcode_sector['properties']['pop_density_km2'], float):
                yield postcode_sector


def import_sitefinder_data(path):
    """
    Import sitefinder data, selecting desired asset types.
        - Select sites belonging to main operators:
            - Includes 'O2', 'Vodafone', BT EE (as 'Orange'/'T-Mobile') and 'Three'
            - Excludes 'Airwave' and 'Network Rail'
        - Select relevant cells:
            - Includes 'Macro', 'SECTOR', 'Sectored' and 'Directional'
            - Excludes 'micro', 'microcell', 'omni' or 'pico' antenna types.

    """
    asset_data = []

    site_id = 0

    with open(os.path.join(path), 'r') as system_file:
        reader = csv.DictReader(system_file)
        next(reader, None)
        for line in reader:
            if line['Operator'] != 'Airwave' and line['Operator'] != 'Network Rail':
            # if line['Operator'] == 'O2' or line['Operator'] == 'Vodafone':
                # if line['Anttype'] == 'MACRO' or \
                #     line['Anttype'] == 'SECTOR' or \
                #     line['Anttype'] == 'Sectored' or \
                #     line['Anttype'] == 'Directional':
                asset_data.append({
                    'type': "Feature",
                    'geometry': {
                        "type": "Point",
                        "coordinates": [float(line['X']), float(line['Y'])]
                    },
                    'properties':{
                        'name': 'site_' + str(site_id),
                        'Operator': line['Operator'],
                        'Opref': line['Opref'],
                        'Sitengr': line['Sitengr'],
                        'Antennaht': line['Antennaht'],
                        'Transtype': line['Transtype'],
                        'Freqband': line['Freqband'],
                        'Anttype': line['Anttype'],
                        'Powerdbw': line['Powerdbw'],
                        'Maxpwrdbw': line['Maxpwrdbw'],
                        'Maxpwrdbm': line['Maxpwrdbm'],
                        'Sitelat': float(line['Sitelat']),
                        'Sitelng': float(line['Sitelng']),
                    }
                })

            site_id += 1

        else:
            pass

    return asset_data


def process_asset_data(data):
    """
    Add buffer to each site, dissolve overlaps and take centroid.

    """
    buffered_assets = []

    for asset in data:
        asset_geom = shape(asset['geometry'])
        buffered_geom = asset_geom.buffer(50)

        asset['buffer'] = buffered_geom
        buffered_assets.append(asset)

    output = []
    assets_seen = set()

    for asset in tqdm(buffered_assets):
        if asset['properties']['Opref'] in assets_seen:
            continue
        assets_seen.add(asset['properties']['Opref'])
        touching_assets = []
        for other_asset in buffered_assets:
            if asset['buffer'].intersects(other_asset['buffer']):
                touching_assets.append(other_asset)
                assets_seen.add(other_asset['properties']['Opref'])

        dissolved_shape = cascaded_union([a['buffer'] for a in touching_assets])
        final_centroid = dissolved_shape.centroid
        output.append({
            'type': "Feature",
            'geometry': {
                "type": "Point",
                "coordinates": [final_centroid.coords[0][0], final_centroid.coords[0][1]],
            },
            'properties':{
                'name': asset['properties']['name'],
            }
        })

    return output


def add_coverage_to_sites(sitefinder_data, postcode_sectors):

    final_sites = []

    idx = index.Index(
        (i, shape(site['geometry']).bounds, site)
        for i, site in enumerate(sitefinder_data)
    )

    for postcode_sector in tqdm(postcode_sectors):
        for n in idx.intersection((shape(postcode_sector['geometry']).bounds), objects=True):
            postcode_sector_shape = shape(postcode_sector['geometry'])
            site_shape = shape(n.object['geometry'])
            if postcode_sector_shape.intersects(site_shape):
                final_sites.append({
                    'id': postcode_sector['properties']['id'],
                    'name': n.object['properties']['name'],
                    'lte_4G': postcode_sector['properties']['lte'],
                    'easting': site_shape.x,
                    'northing': site_shape.y,
                })

    return final_sites


def convert_postcode_sectors_to_list(data):

    data_for_writing = []
    for datum in data:
        data_for_writing.append({
            'id': datum['properties']['id'],
            'lad': datum['properties']['lad'],
            'population': datum['properties']['population'],
            'area_km2': datum['properties']['area_km2'],
            'pop_density_km2': datum['properties']['pop_density_km2'],
            'lte_4G': datum['properties']['lte'],

        })

    return data_for_writing


def csv_writer(data, directory, filename):
    """
    Write data to a CSV file path

    """
    # Create path
    if not os.path.exists(directory):
        os.makedirs(directory)

    fieldnames = []
    for name, value in data[0].items():
        fieldnames.append(name)

    with open(os.path.join(directory, filename), 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames, lineterminator = '\n')
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":

    start = time.time()

    directory_intermediate = os.path.join(DATA_INTERMEDIATE)
    print('Output directory will be {}'.format(directory_intermediate))

    print('Loading local authority district shapes')
    lads = read_lads()

    print('Loading lad lookup')
    lad_lut = lad_lut(lads)

    print('Loading postcode sector shapes')
    path = os.path.join(DATA_RAW, 'shapes', 'PostalSector.shp')
    postcode_sectors = read_postcode_sectors(path)

    print('Adding lad IDs to postcode sectors... might take a few minutes...')
    postcode_sectors = add_lad_to_postcode_sector(postcode_sectors, lads)

    print('Subset Arc shapes')
    directory_shapes = os.path.join(DATA_RAW, 'shapes')
    write_arc_shapes(postcode_sectors, 'arc_postcode_sectors.shp', directory_shapes)

    print('Loading in population weights' )
    weights = load_in_weights()

    print('Adding weights to postcode sectors')
    postcode_sectors = add_weights_to_postcode_sector(postcode_sectors, weights)

    print('Calculating lad population weight for each postcode sector')
    postcode_sectors = calculate_lad_population(postcode_sectors)

    print('Generating scenario variants')
    generate_scenario_variants(postcode_sectors, directory_intermediate)

    print('Disaggregate 4G coverage to postcode sectors')
    postcode_sectors = allocate_4G_coverage(postcode_sectors, lad_lut)

    print('Importing sitefinder data')
    folder = os.path.join(DATA_RAW, 'sitefinder')
    sitefinder_data = import_sitefinder_data(os.path.join(folder, 'sitefinder.csv'))

    print('Preprocessing sitefinder data with 50m buffer')
    sitefinder_data = process_asset_data(sitefinder_data)

    print('Allocate 4G coverage to sites from postcode sectors')
    processed_sites = add_coverage_to_sites(sitefinder_data, postcode_sectors)

    print('Convert geojson postcode sectors to list of dicts')
    postcode_sectors = convert_postcode_sectors_to_list(postcode_sectors)

    print('Specifying clutter geotypes')
    geotypes = [
        {'geotype': 'urban', 'population_density': 7959},
        {'geotype': 'suburban', 'population_density': 782},
        {'geotype': 'rural', 'population_density': 0},
    ]
    csv_writer(geotypes, directory_intermediate, 'lookup_table_geotype.csv')

    print('Writing postcode sectors to .csv')
    csv_writer(postcode_sectors, directory_intermediate, '_processed_postcode_sectors.csv')

    print('Writing processed sites to .csv')
    csv_writer(processed_sites, directory_intermediate, 'final_processed_sites.csv')

    end = time.time()
    print('time taken: {} minutes'.format(round((end - start) / 60,2)))
