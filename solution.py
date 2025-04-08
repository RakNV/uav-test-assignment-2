from decimal import Decimal, getcontext
from typing import Tuple
import math

DECIMAL_PRECISION = 8
getcontext().prec = DECIMAL_PRECISION
EARTH_RADIUS_M    = 111_000
RIGHT_ANGLE_DEG   = 90
HALF_CIRCLE_DEG   = 180
FULL_CIRCLE_DEG   = 360


def calculate_image_center(
    point_coord: Tuple[Decimal, Decimal],
    azimuth: int,
    center_px: Tuple[int, int],
    point_px: Tuple[int, int],
    scale: float
) -> Tuple[Decimal, Decimal]:
    print("=== Step-by-step Image Center Calculation ===")

    # Step 1: Calculate pixel difference (X and Y)
    delta_x_px = point_px[0] - center_px[0]
    delta_y_px = point_px[1] - center_px[1]
    print(f"ΔX in pixels: {delta_x_px}")
    print(f"ΔY in pixels: {delta_y_px}")

    # Step 2: Convert pixel shift to meters
    delta_x_m = delta_x_px * scale
    delta_y_m = delta_y_px * scale
    print(f"ΔX in meters: {delta_x_m}")
    print(f"ΔY in meters: {delta_y_m}")

    # Step 3: Determine azimuth directions for X (right) and Y (down)
    azimuth_right = (azimuth + RIGHT_ANGLE_DEG) % FULL_CIRCLE_DEG
    azimuth_down = (azimuth + HALF_CIRCLE_DEG) % FULL_CIRCLE_DEG
    print(f"Azimuth right: {azimuth_right}°")
    print(f"Azimuth down: {azimuth_down}°")

    # Step 4: Project X and Y distances into east/north components
    east_x = delta_x_m * math.sin(math.radians(azimuth_right))
    north_x = delta_x_m * math.cos(math.radians(azimuth_right))
    print(f"East from ΔX: {east_x}")
    print(f"North from ΔX: {north_x}")

    east_y = delta_y_m * math.sin(math.radians(azimuth_down))
    north_y = delta_y_m * math.cos(math.radians(azimuth_down))
    print(f"East from ΔY: {east_y}")
    print(f"North from ΔY: {north_y}")

    # Step 5: Total shift in meters
    total_east = east_x + east_y
    total_north = north_x + north_y
    print(f"Total East shift (m): {total_east}")
    print(f"Total North shift (m): {total_north}")

    # Step 6: Convert meter shifts to lat/lon degrees
    delta_lat = total_north / EARTH_RADIUS_M
    lat_rad = math.radians(float(point_coord[0]))
    delta_lon = total_east / (EARTH_RADIUS_M * math.cos(lat_rad))
    print(f"Latitude shift in degrees: {delta_lat}")
    print(f"Longitude shift in degrees: {delta_lon}")

    # Step 7: Subtract shift from point coordinates to get center
    center_lat = point_coord[0] - Decimal(str(delta_lat))
    center_lon = point_coord[1] - Decimal(str(delta_lon))
    print(f"Calculated center latitude: {center_lat}")
    print(f"Calculated center longitude: {center_lon}")

    return (center_lat, center_lon)


def main() -> None:

    point_coord = (Decimal('50.603694'), Decimal('30.650625'))
    azimuth     = 335
    resolution  = (640, 512)
    center_px   = (320, 256)
    point_px    = (558, 328)
    scale       = 0.38  # 1 px = 0.38m 

    center_lat, center_lon = calculate_image_center(
        point_coord=point_coord,
        azimuth=azimuth,
        center_px=center_px,
        point_px=point_px,
        scale=scale
    )

    print("\n=== Final Result ===")
    print(f"Image center coordinates: {center_lat}, {center_lon}")

if __name__ == "__main__":
    main()