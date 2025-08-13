#!/usr/bin/env python3
import sys
import os
import math
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import simplekml

def parse_first_polygon_coords(kml_path):
    # Parse XML with namespace wildcards
    tree = ET.parse(kml_path)
    root = tree.getroot()
    # Find the first <Polygon>
    polygon = root.find(".//{*}Polygon")
    if polygon is None:
        return None, None, None  # name, coords, docroot

    # Try to get the containing placemark name (if any)
    placemark = polygon
    name_text = ""
    # Walk up parents is not straightforward in ElementTree; instead search for a Placemark containing this polygon
    # We'll do a second pass to find the first Placemark that contains a Polygon.
    placemark = root.find(".//{*}Placemark[{*}Polygon]")
    if placemark is not None:
        name_el = placemark.find("{*}name")
        if name_el is not None and name_el.text:
            name_text = name_el.text.strip()

    coords_el = polygon.find(".//{*}outerBoundaryIs//{*}LinearRing//{*}coordinates")
    if coords_el is None or not (coords_el.text and coords_el.text.strip()):
        # Sometimes coordinates are directly under Polygon (rare), try a generic search
        coords_el = polygon.find(".//{*}coordinates")

    if coords_el is None or not (coords_el.text and coords_el.text.strip()):
        return name_text, None, root

    coords_text = coords_el.text.strip()
    # KML: "lon,lat[,alt]" tuples separated by whitespace
    coords = []
    for token in coords_text.replace("\n", " ").replace("\t", " ").split():
        parts = token.split(",")
        if len(parts) >= 2:
            try:
                lon = float(parts[0])
                lat = float(parts[1])
                coords.append((lon, lat))
            except ValueError:
                continue

    # Ensure polygon is valid for centroid computation (at least 3 points)
    if len(coords) < 3:
        return name_text, None, root
    return name_text, coords, root

def polygon_centroid(coords):
    # 2D polygon centroid (lon, lat) using shoelace formula; expects non-self-intersecting polygon
    # If first point repeats at end, ignore the duplicate.
    if coords[0] == coords[-1]:
        pts = coords[:-1]
    else:
        pts = coords
    A = 0.0
    Cx = 0.0
    Cy = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        cross = x1 * y2 - x2 * y1
        A += cross
        Cx += (x1 + x2) * cross
        Cy += (y1 + y2) * cross
    A *= 0.5
    if abs(A) < 1e-12:
        # Degenerate polygon
        # Fallback: average of vertices
        sx = sum(p[0] for p in pts)
        sy = sum(p[1] for p in pts)
        return sx / n, sy / n
    Cx /= (6.0 * A)
    Cy /= (6.0 * A)
    return Cx, Cy

def generate_crosshair_icon(icon_path):
    # Generate a simple crosshair icon
    fig, ax = plt.subplots(figsize=(0.5, 0.5), dpi=100)
    ax.plot([0.1, 0.9], [0.5, 0.5], linewidth=2)  # Horizontal
    ax.plot([0.5, 0.5], [0.1, 0.9], linewidth=2)  # Vertical
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    plt.savefig(icon_path, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close(fig)

def add_placemark_with_icon(kml_path, name, latitude, longitude):
    # Generate the crosshair icon and save to a file next to the input KML
    icon_path = os.path.join(os.path.dirname(kml_path), "centroid_crosshair.png")
    generate_crosshair_icon(icon_path)

    # Create a new KML object to add the placemark with the custom icon
    kml_obj = simplekml.Kml()
    placemark = kml_obj.newpoint(name=" ", coords=[(longitude, latitude)])
    placemark.description = f"{name} centroid"
    placemark.style.iconstyle.icon.href = icon_path
    placemark.style.iconstyle.scale = 1.2  # Adjust the size of the icon

    # Save the placemark KML file separately
    title = os.path.splitext(os.path.basename(kml_path))[0]
    centroid_kml_path = os.path.join(os.path.dirname(kml_path), f"{title}_centroid.kml")
    kml_obj.save(centroid_kml_path)
    print(f"Centroid placemark saved as {centroid_kml_path}")

def main():
    if len(sys.argv) == 2:
        kml_path = sys.argv[1]
    else:
        kml_path = input("Enter kml location: ").strip()

    try:
        name, coords, _ = parse_first_polygon_coords(kml_path)
        if not coords:
            raise ValueError("The KML file does not contain a Polygon with coordinates.")
        lon, lat = polygon_centroid(coords)
        # Print centroid in "lat,lon"
        print(f"{lat},{lon}")
        add_placemark_with_icon(kml_path, name or "", lat, lon)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
