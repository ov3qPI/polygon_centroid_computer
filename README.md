# polygon_centroid_computer
Calculates the centroid of a polygon from a given KML file

## Requirements

- Python 3
- `shapely` library
- `fastkml` library
- `pygeoif` library

Install dependencies via pip:
```sh
pip install shapely fastkml pygeoif
```

## Usage

To run the script, use the following command:
```sh
./g_earth_polygon_centroid_computer.py <path_to_kml_file>
```

### Output

The script prints the centroid coordinates `(x, y)` of the first polygon found in the KML file.

## Example
```sh
./g_earth_polygon_centroid_computer.py example.kml
Centroid: (longitude, latitude)
```

## Error Handling

- If no polygon is found, a `ValueError` is raised.
- If an incorrect number of arguments is provided, usage instructions are printed.

## Notes

- The script examines KML files for Placemarks containing polygon geometry and computes the centroid of the first polygon found.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

