#!/usr/bin/env python3
import sys
from shapely.geometry import Polygon
from fastkml import kml
from fastkml.geometry import Geometry
from pygeoif import geometry as pygeoif_geometry

def extract_polygons(features):
    for feature in features:
        print(f"Examining feature: {feature.name}, type: {type(feature)}")
        if isinstance(feature, kml.Placemark):
            geom = feature.geometry
            print(f"Placemark geometry type: {type(geom)}")
            if isinstance(geom, pygeoif_geometry.Polygon):
                return geom
            elif isinstance(geom, Geometry):
                inner_geom = geom.geometry
                print(f"Inner geometry type: {type(inner_geom)}")
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
    print("Top-level features:")
    for feature in features:
        print(f"Feature: {feature.name}, type: {type(feature)}")

    polygon = extract_polygons(features)
    if not polygon:
        raise ValueError("The KML file does not contain a Polygon.")

    # Convert pygeoif.geometry.Polygon to shapely.geometry.Polygon
    exterior_coords = list(polygon.exterior.coords)
    poly = Polygon(exterior_coords)
    centroid = poly.centroid
    return centroid.x, centroid.y

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: g_earth_polygon_centroid_computer.py <path_to_kml_file>")
        sys.exit(1)

    kml_path = sys.argv[1]
    try:
        centroid_x, centroid_y = compute_centroid(kml_path)
        print(f"Centroid: ({centroid_x}, {centroid_y})")
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)
