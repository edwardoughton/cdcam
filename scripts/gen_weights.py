import os
import sys
import configparser
import csv
import fiona
import time
import glob

from shapely.geometry import shape, Point, Polygon, mapping
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
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'shapes', 'codepoint', 'intermediate')

#####################################
# READ MAIN DATA
#####################################

def load_codepoint_data(path):

    output = []

    # PC PQ	PR	TP	DQ	RP	BP	PD	MP	UM	EA	NO	CY	RH	LH	CC	DC	WC	LS
    # Postcode	Positional_quality_indicator	PO_Box_indicator
    # Total_number_of_delivery_points	Delivery_points_used_to_create_the_CPLC
    # Domestic_delivery_points	Non_domestic_delivery_points	PO_Box_delivery_points
    # Matched_address_premises	Unmatched_delivery_points	Eastings	Northings
    # Country_code	NHS_regional_HA_code	NHS_HA_code	Admin_county_code
    # Admin_district_code	Admin_ward_code	Postcode_type

    with open(path, 'r') as source:
        reader = csv.reader(source)
        for line in reader:
            output.append({
                'type': 'Point',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [float(line[10]),float(line[11])]
                },
                'properties': {
                    'postcode': line[0],
                    'Domestic_delivery_points': line[5],
                }
            })

    return output


def read_postcode_sectors(path):
    """
    Read all postcode sector shapes.

    """
    with fiona.open(path, 'r') as pcd_sector_shapes:
        return [pcd for pcd in pcd_sector_shapes]


def intersect_areas(postcode_sectors, postcodes):

    idx = index.Index(
        (i, shape(postcode_sector['geometry']).bounds, postcode_sector)
        for i, postcode_sector in enumerate(postcode_sectors)
    )

    processed = []

    for postcode in tqdm(postcodes):
        for n in idx.intersection((shape(postcode['geometry']).bounds), objects=True):
            postcode_centroid = shape(postcode['geometry'])
            postcode_sector_shape = shape(n.object['geometry'])
            if postcode_centroid.intersects(postcode_sector_shape):
                processed.append({
                        'postcode': postcode['properties']['postcode'],
                        'Domestic_delivery_points': postcode['properties']['Domestic_delivery_points'],
                        'RMSect': n.object['properties']['RMSect'],
                    })

    return processed


def load_processed_data(paths):

    output = []

    for path in paths:
        with open(path, 'r') as source:
            reader = csv.DictReader(source)
            for line in reader:
                output.append({
                    'postcode_sector': line['RMSect'],
                    'domestic_delivery_points': line['Domestic_delivery_points'],
                })

    return output


def aggregate(postcode_sectors):

    unique_pcd_sectors = set()

    for postcode in postcode_sectors:
        unique_pcd_sectors.add(postcode['postcode_sector'])

    output = []

    for pcd_sector in tqdm(unique_pcd_sectors):
        domestic_delivery_points = 0
        for item in postcode_sectors:
            if pcd_sector == item['postcode_sector']:
                domestic_delivery_points += int(item['domestic_delivery_points'])
        output.append({
            'postcode_sector': pcd_sector,
            'domestic_delivery_points': domestic_delivery_points
        })

    return output


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

    print('load postcode sectors')
    path = os.path.join(DATA_RAW, 'shapes', 'PostalSector.shp')
    postcode_sectors = read_postcode_sectors(path)

    print('getting codepoint path names')
    paths = glob.glob(os.path.join(DATA_RAW, 'codepoint_data', '*.csv'))

    for path in paths:

        codepoint_data = load_codepoint_data(path)

        postcode_sector_lut = intersect_areas(postcode_sectors, codepoint_data)

        directory = os.path.join(DATA_RAW, 'intermediate', 'codepoint')
        csv_writer(postcode_sector_lut, directory, os.path.basename(path))

    paths = glob.glob(os.path.join(DATA_RAW, 'intermediate', 'codepoint', '*.csv'))

    print('loading processed csv data')
    codepoint_data = load_processed_data(paths)

    print('aggregating data')
    aggregated_data = aggregate(codepoint_data)

    print('writing data to csv')
    directory = os.path.join(DATA_RAW, 'intermediate')
    csv_writer(aggregated_data, directory, 'population_weights.csv')

    end = time.time()
    print('time taken: {} minutes'.format(round((end - start) / 60,2)))
