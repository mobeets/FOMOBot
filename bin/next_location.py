from collections import namedtuple
from random import choice
import csv

INFILE = 'locs.csv'
BIG_CITIES_FILE = 'loc_pops.csv'
RNG = 0.025

HEADER = 'locId,country,region,city,postalCode,latitude,longitude,metroCode,areaCode'
Location = namedtuple('Location', HEADER)

def location(infile=INFILE, bigfile=BIG_CITIES_FILE):
    with open(bigfile, 'rb') as csvfile:
        rows = list(csv.reader(csvfile))
        city, state = choice(rows)

    with open(infile, 'rb') as csvfile:
        rows = list(csv.reader(csvfile))
        for row in rows:
            loc = Location(*row)
            if not loc.latitude:
                continue
            if loc.city.lower() == city.lower():
                if loc.region == state:
                    return loc

def bounding_box(loc, rng=RNG):
    lat, lon = float(loc.latitude), float(loc.longitude)
    lat_1, lat_2 = lat - rng, lat + rng
    lon_1, lon_2 = lon - rng, lon + rng
    return [lon_1, lat_1, lon_2, lat_2]
