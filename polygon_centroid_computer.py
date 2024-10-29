#!/usr/bin/env python3
import sys
import logging
from shapely.geometry import Polygon
from fastkml import kml
from fastkml.geometry import Geometry
from pygeoif import geometry as pygeoif_geometry

logging.basicConfig(level=logging.WARNING)

def extract_polygons(features):
    for feature in features:
        if isinstance(feature, kml.Placemark):
            geom = feature.geometry
            if isinstance(geom, pygeoif_geometry.Polygon):
                return geom
            elif isinstance(geom, Geometry):
                inner_geom = geom.geometry
                if isinstance(inner_geom, pygeoif_geometry.Polygon):
                    return inner_geom
        if hasattr(feature, 'features'):
            result = extract_polygons(feature.features())
            if result:
                return result
    return None

def compute_centroid(kml_path):
    with open(kml_path, 'rb') as file:
        doc = file.read()

    k = kml.KML()
    k.from_string(doc)

    features = list(k.features())
    polygon = extract_polygons(features)
    if not polygon:
        raise ValueError("The KML file does not contain a Polygon.")

    # Convert pygeoif.geometry.Polygon to shapely.geometry.Polygon
    exterior_coords = list(polygon.exterior.coords)
    poly = Polygon(exterior_coords)
    centroid = poly.centroid
    return centroid.x, centroid.y

if __name__ == "__main__":
    if len(sys.argv) == 2:
        kml_path = sys.argv[1]
    else:
        kml_path = input("Enter kml location: ")

    try:
        centroid_x, centroid_y = compute_centroid(kml_path)
        # Print centroid in a Google Earth compatible format with altitude 0
        print(f"{centroid_y},{centroid_x}")
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)
