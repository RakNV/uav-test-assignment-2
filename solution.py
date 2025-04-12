from decimal import Decimal, getcontext
from typing import Tuple
import math

# Constants
DECIMAL_PRECISION = 8
getcontext().prec = DECIMAL_PRECISION

EARTH_RADIUS_M = 111_000
RIGHT_ANGLE_DEG = 90
HALF_CIRCLE_DEG = 180
FULL_CIRCLE_DEG = 360


def pixel_to_meter_shift(
    center_px: Tuple[int, int],
    point_px: Tuple[int, int],
    scale: float
) -> Tuple[float, float]:
    """
    Converts the pixel offset between a known point and image center into meter displacement.

    :param center_px: Pixel coordinates of the image center (x, y).
    :param point_px: Pixel coordinates of the known point (x, y).
    :param scale: Physical size of one pixel in meters.
    :return: Tuple (dx, dy) displacement in meters.
    """
    dx = (point_px[0] - center_px[0]) * scale
    dy = (point_px[1] - center_px[1]) * scale
    print(f"[1] Pixel shift: Δx = {point_px[0] - center_px[0]}, Δy = {point_px[1] - center_px[1]}")
    print(f"[2] Converted to meters: dx = {dx:.4f} m, dy = {dy:.4f} m")
    return dx, dy


def project_shift(
    dx: float,
    dy: float,
    azimuth: int
) -> Tuple[float, float]:
    """
    Projects displacements (in image X/Y meters) into geographic east/north directions based on azimuth.

    :param dx: Displacement in meters along image X-axis.
    :param dy: Displacement in meters along image Y-axis.
    :param azimuth: Camera azimuth in degrees (0° = North, clockwise).
    :return: Tuple (east, north) in meters.
    """
    azimuth_right = (azimuth + RIGHT_ANGLE_DEG) % FULL_CIRCLE_DEG
    azimuth_down = (azimuth + HALF_CIRCLE_DEG) % FULL_CIRCLE_DEG
    print(f"[3] Projected azimuths: right = {azimuth_right}°, down = {azimuth_down}°")

    east = dx * math.sin(math.radians(azimuth_right)) + dy * math.sin(math.radians(azimuth_down))
    north = dx * math.cos(math.radians(azimuth_right)) + dy * math.cos(math.radians(azimuth_down))
    print(f"[4] Projected shift to geographic coordinates: east = {east:.4f} m, north = {north:.4f} m")

    return east, north


def meter_shift_to_geo_shift(
    lat: Decimal,
    east: float,
    north: float
) -> Tuple[float, float]:
    """
    Converts east/north displacements in meters into latitude and longitude shifts.

    :param lat: Latitude at the reference point (in decimal degrees).
    :param east: Eastward displacement in meters.
    :param north: Northward displacement in meters.
    :return: Tuple (delta_lat, delta_lon) in degrees.
    """
    delta_lat = north / EARTH_RADIUS_M
    lat_rad = math.radians(float(lat))
    delta_lon = east / (EARTH_RADIUS_M * math.cos(lat_rad))
    print(f"[5] Converted to geographic shift: Δlat = {delta_lat:.8f}°, Δlon = {delta_lon:.8f}°")
    return delta_lat, delta_lon


def apply_geo_shift(
    lat: Decimal,
    lon: Decimal,
    dlat: float,
    dlon: float
) -> Tuple[Decimal, Decimal]:
    """
    Applies latitude and longitude shifts to compute new coordinates.

    :param lat: Original latitude in decimal degrees.
    :param lon: Original longitude in decimal degrees.
    :param dlat: Latitude shift in degrees.
    :param dlon: Longitude shift in degrees.
    :return: Tuple (new_lat, new_lon) in decimal degrees.
    """
    new_lat = lat - Decimal(str(dlat))
    new_lon = lon - Decimal(str(dlon))
    print(f"[6] Final coordinates after shift: lat = {new_lat}, lon = {new_lon}")
    return new_lat, new_lon


def calculate_image_center_coordinates(
    point_coord: Tuple[Decimal, Decimal],
    azimuth: int,
    center_px: Tuple[int, int],
    point_px: Tuple[int, int],
    scale: float
) -> Tuple[Decimal, Decimal]:
    """
    Calculates geographic coordinates of the image center based on a known point,
    pixel offsets, scale, and camera azimuth.

    :param point_coord: Coordinates (lat, lon) of a known point in the image.
    :param azimuth: Camera azimuth in degrees (0° = North, clockwise).
    :param center_px: Pixel coordinates of the image center (x, y).
    :param point_px: Pixel coordinates of the known point (x, y).
    :param scale: Physical size of one pixel in meters.
    :return: Coordinates (lat, lon) of the image center.
    """
    dx_m, dy_m = pixel_to_meter_shift(center_px, point_px, scale)
    east, north = project_shift(dx_m, dy_m, azimuth)
    delta_lat, delta_lon = meter_shift_to_geo_shift(point_coord[0], east, north)
    return apply_geo_shift(point_coord[0], point_coord[1], delta_lat, delta_lon)


def main() -> None:
    print("=== Computing image center coordinates step-by-step ===")
    point_coord = (Decimal('50.603694'), Decimal('30.650625'))
    azimuth = 335
    center_px = (320, 256)
    point_px = (558, 328)
    scale = 0.38
    print(f"[0] Input data:\n"
          f"- Known point coordinates: {point_coord}\n"
          f"- Azimuth: {azimuth}°\n"
          f"- Image center (px): {center_px}\n"
          f"- Known point (px): {point_px}\n"
          f"- Pixel scale: {scale} m/pixel\n")

    center_lat, center_lon = calculate_image_center_coordinates(
        point_coord=point_coord,
        azimuth=azimuth,
        center_px=center_px,
        point_px=point_px,
        scale=scale
    )

    print("=== Final Result ===")
    print(f"Image center coordinates: {center_lat}, {center_lon}")

if __name__ == "__main__":
    main()