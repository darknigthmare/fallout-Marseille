"""Compare the conservative sweep with the previous exhaustive validator.

The reference deliberately keeps the old pair loops. It uses the same exact
segment predicate and establishes accept/reject parity, without timing limits.
"""
import copy
import math
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
import world_sources as source


def exhaustive_ring(raw, crs, counter):
    if not isinstance(raw, list) or not 4 <= len(raw) <= source.MAX_RING_VERTICES:
        raise source.SourceError(f'polygon rings require 4..{source.MAX_RING_VERTICES} vertices')
    ring = [source.position(p, crs) for p in raw]
    counter[0] += len(ring)
    if counter[0] > source.MAX_VERTICES:
        raise source.SourceError('source exceeds the vertex budget')
    if ring[0] != ring[-1]:
        raise source.SourceError('polygon ring is not closed; no implicit closing edge is added')
    if any(a[:2] == b[:2] for a, b in zip(ring, ring[1:])):
        raise source.SourceError('polygon ring contains a zero-length edge')
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:])) / 2
    if abs(area) < 1e-14:
        raise source.SourceError('polygon ring has zero area')
    count = len(ring) - 1
    for i in range(count):
        for j in range(i + 2, count):
            if i == 0 and j == count - 1:
                continue
            if source._segments_intersect(ring[i], ring[i + 1], ring[j], ring[j + 1]):
                raise source.SourceError('polygon ring self-intersects')
    return ring


def exhaustive_polygon(raw, crs, counter):
    if not isinstance(raw, list) or not raw:
        raise source.SourceError('polygon has no outer ring')
    rings = [exhaustive_ring(ring, crs, counter) for ring in raw]
    for i, hole in enumerate(rings[1:], 1):
        if not source._point_inside(rings[0], hole[0]):
            raise source.SourceError('polygon hole is not strictly inside its outer ring')
        for previous in rings[:i]:
            if any(source._segments_intersect(a, b, c, d)
                   for a, b in zip(hole, hole[1:]) for c, d in zip(previous, previous[1:])):
                raise source.SourceError('polygon rings intersect or touch')
        if any(source._point_inside(previous, hole[0]) or source._point_inside(hole, previous[0])
               for previous in rings[1:i]):
            raise source.SourceError('polygon holes overlap or are nested')
    return rings


def result(function, raw, crs='EPSG:4326', count=0):
    counter = [count]
    try:
        return 'accepted', function(raw, crs, counter), counter[0]
    except source.SourceError as error:
        return 'rejected', str(error), counter[0]


def close(points):
    return points + [points[0][:]]


def ellipse(count, radius=1, center=(5, 43)):
    return close([[center[0] + radius * math.cos(i * math.tau / count),
                   center[1] + radius * .7 * math.sin(i * math.tau / count)] for i in range(count)])


class GeometryBroadphaseTests(unittest.TestCase):
    def assertRingParity(self, ring, crs='EPSG:4326', count=0):
        original = copy.deepcopy(ring)
        self.assertEqual(result(source._ring, ring, crs, count), result(exhaustive_ring, ring, crs, count))
        self.assertEqual(ring, original)

    def assertPolygonParity(self, polygon):
        original = copy.deepcopy(polygon)
        self.assertEqual(result(source._polygon, polygon), result(exhaustive_polygon, polygon))
        self.assertEqual(polygon, original)

    def test_concave_and_self_crossing_rings_keep_original_decisions(self):
        cases = [
            close([[0, 0], [6, 0], [6, 2], [2, 2], [2, 5], [0, 5]]),
            close([[0, 0], [5, 4], [0, 5], [4, 0]]),
            close([[0, 0], [5, 0], [5, 5], [2, 2], [0, 5]]),
            close([[0, 0], [4, 0], [2, 0], [4, 4], [0, 4]]),
            close([[0, 0], [4, 0], [4, 4], [2, 0], [0, 4]]),
            close([[0, 0], [4, 0], [4, 4], [0, 4], [4, 0]]),
        ]
        for ring in cases:
            with self.subTest(ring=ring):
                self.assertRingParity(ring)

    def test_holes_outside_touching_crossing_nested_and_disjoint_keep_decisions(self):
        outer = close([[0, 0], [20, 0], [20, 20], [12, 20], [12, 12], [8, 12], [8, 20], [0, 20]])
        cases = [
            [outer, close([[2, 2], [4, 2], [4, 4], [2, 4]])],
            [outer, close([[-1, 2], [2, 2], [2, 4], [-1, 4]])],
            [outer, close([[0, 2], [2, 2], [2, 4], [0, 4]])],
            [outer, close([[5, 5], [15, 5], [15, 15], [5, 15]])],
            [outer, close([[2, 2], [7, 2], [7, 7], [2, 7]]), close([[3, 3], [4, 3], [4, 4], [3, 4]])],
            [outer, close([[2, 2], [7, 2], [7, 7], [2, 7]]), close([[6, 6], [9, 6], [9, 9], [6, 9]])],
            [outer, close([[2, 2], [4, 2], [4, 4], [2, 4]]), close([[14, 2], [16, 2], [16, 4], [14, 4]])],
        ]
        for polygon in cases:
            with self.subTest(polygon=polygon):
                self.assertPolygonParity(polygon)

    def test_seeded_random_simple_and_permuted_rings_match_exhaustive(self):
        rng = random.Random(13055)
        for iteration in range(500):
            count = rng.randrange(3, 42)
            angles = sorted(rng.random() * math.tau for _ in range(count))
            scale = rng.choice([1, .01, .00001])
            points = [[5 + scale * (.3 + rng.random()) * math.cos(a),
                       43 + scale * (.3 + rng.random()) * math.sin(a)] for a in angles]
            if iteration % 2:
                rng.shuffle(points)
            with self.subTest(iteration=iteration):
                self.assertRingParity(close(points))

    def test_near_collinear_endpoints_keep_every_tolerant_exact_intersection(self):
        rng = random.Random(6900)
        for origin in [0, 5, 43, 179]:
            for _ in range(100):
                first = [[origin + i * 1e-12, (rng.randrange(-2, 3)) * 1e-14] for i in range(5)]
                second = [[origin + i * 1e-12 + rng.choice([-1, 0, 1]) * 1e-14,
                           rng.choice([-2, -1, 0, 1, 2]) * 1e-14] for i in range(5)]
                candidates = set(source._segment_candidates(first, second))
                for i, (a, b) in enumerate(zip(first, first[1:])):
                    for j, (c, d) in enumerate(zip(second, second[1:])):
                        if source._segments_intersect(a, b, c, d):
                            self.assertIn((i, j), candidates)

    def test_seeded_cross_ring_candidates_are_a_superset_of_exact_hits(self):
        rng = random.Random(2154)
        for _ in range(250):
            first = [[rng.uniform(-5, 5), rng.uniform(-5, 5)] for _ in range(20)]
            second = [[rng.uniform(-5, 5), rng.uniform(-5, 5)] for _ in range(20)]
            expected = any(source._segments_intersect(a, b, c, d)
                           for a, b in zip(first, first[1:]) for c, d in zip(second, second[1:]))
            self.assertEqual(source._rings_intersect(first, second), expected)
            candidates = set(source._segment_candidates(first, second))
            for i, (a, b) in enumerate(zip(first, first[1:])):
                for j, (c, d) in enumerate(zip(second, second[1:])):
                    if source._segments_intersect(a, b, c, d):
                        self.assertIn((i, j), candidates)

    def test_large_complex_ring_and_late_crossing_match_exhaustive(self):
        ring = ellipse(1024, .01)
        self.assertRingParity(ring)
        ring[850] = ring[220][:]
        self.assertRingParity(ring)

    def test_large_outer_ring_and_hole_keep_full_coordinates(self):
        self.assertPolygonParity([ellipse(700, .01), ellipse(300, .004)])

    def test_broadphase_prunes_large_simple_curve_without_changing_predicate(self):
        ring = ellipse(2047, .01)
        candidates = list(source._segment_candidates(ring))
        self.assertLess(len(candidates), 2047)
        self.assertEqual(source._ring(ring, 'EPSG:4326', [0]), ring)

    def test_vertex_budget_z_closure_and_degenerate_errors_are_unchanged(self):
        for ring in [[], [[0, 0]] * 4, [[0, 0], [1, 0], [0, 1], [0, 2]],
                     [[0, 0, 1], [1, 0, 2], [0, 1, 3], [0, 0, 2]],
                     ellipse(2048), close([[0, 0], [1, 0], [0, 1]])]:
            self.assertRingParity(ring, count=source.MAX_VERTICES - 3)


if __name__ == '__main__':
    unittest.main()
