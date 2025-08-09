import cv2
import numpy as np
from shapely.ops import unary_union, voronoi_diagram
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection, Point

def make_polygon(img_p):
    img = cv2.imread(img_p, cv2.IMREAD_UNCHANGED)
    alpha = img[..., 3]
    mask_a = alpha > 0

    num, labels, stats, _ = cv2.connectedComponentsWithStats(
        alpha.astype(np.uint8), connectivity=8
    )

    if num <= 1:
        raise RuntimeError("No painted pixels!")
    biggest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])

    floor_mask = (labels == biggest).astype(np.uint8) * 255

    clean = cv2.morphologyEx(floor_mask, cv2.MORPH_CLOSE,
                             kernel=np.ones((5, 5), np.uint8), iterations=2)

    contours, hier = cv2.findContours(clean, cv2.RETR_CCOMP,
                                      cv2.CHAIN_APPROX_SIMPLE)
    hier = hier[0]

    polys = []
    for idx, cnt in enumerate(contours):
        if hier[idx][3] != -1:
            continue
        cnt = cnt.squeeze()
        if cnt.shape[0] < 4:
            continue
        holes = []
        child = hier[idx][2]
        while child != -1:
            h = contours[child].squeeze()
            if h.shape[0] >= 4:
                holes.append(h)
            child = hier[child][0]
        polys.append(Polygon(cnt, holes))


    return unary_union(polys).buffer(0)

def is_valid_point(point, polygon):
    """Check if a point is within the polygon."""
    if not isinstance(point, Point):
        point = Point(point)
    if isinstance(polygon, (MultiPolygon, GeometryCollection)):
        return any(p.contains(point) for p in polygon.geoms)
    return polygon.contains(point)