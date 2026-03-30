"""Classify each module in a QR matrix by its structural role."""

from __future__ import annotations

from enum import Enum, auto


class ModuleType(Enum):
    DATA = auto()
    FINDER_OUTER = auto()
    FINDER_INNER = auto()
    SEPARATOR = auto()
    TIMING = auto()
    ALIGNMENT_OUTER = auto()
    ALIGNMENT_INNER = auto()
    FORMAT_INFO = auto()
    VERSION_INFO = auto()
    QUIET = auto()


# Alignment pattern center positions per QR version (version 2+).
# From ISO/IEC 18004 Table E.1.
_ALIGNMENT_POSITIONS: dict[int, list[int]] = {
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
    6: [6, 34],
    7: [6, 22, 38],
    8: [6, 24, 42],
    9: [6, 26, 46],
    10: [6, 28, 50],
    11: [6, 30, 54],
    12: [6, 32, 58],
    13: [6, 34, 62],
    14: [6, 26, 46, 66],
    15: [6, 26, 48, 70],
    16: [6, 26, 50, 74],
    17: [6, 30, 54, 78],
    18: [6, 30, 56, 82],
    19: [6, 30, 58, 86],
    20: [6, 34, 62, 90],
    21: [6, 28, 50, 72, 94],
    22: [6, 26, 50, 74, 98],
    23: [6, 30, 54, 78, 102],
    24: [6, 28, 54, 80, 106],
    25: [6, 32, 58, 84, 110],
    26: [6, 30, 58, 86, 114],
    27: [6, 34, 62, 90, 118],
    28: [6, 26, 50, 74, 98, 122],
    29: [6, 30, 54, 78, 102, 126],
    30: [6, 26, 52, 78, 104, 130],
    31: [6, 30, 56, 82, 108, 134],
    32: [6, 34, 60, 86, 112, 138],
    33: [6, 30, 58, 86, 114, 142],
    34: [6, 34, 62, 90, 118, 146],
    35: [6, 30, 54, 78, 102, 126, 150],
    36: [6, 24, 50, 76, 102, 128, 154],
    37: [6, 28, 54, 80, 106, 132, 158],
    38: [6, 32, 58, 84, 110, 136, 162],
    39: [6, 26, 54, 82, 110, 138, 166],
    40: [6, 30, 58, 86, 114, 142, 170],
}


def _version_from_size(size: int) -> int:
    return (size - 17) // 4


def _finder_regions(size: int) -> set[tuple[int, int]]:
    """Return (row, col) set for all three finder pattern areas (7x7 + separators)."""
    coords: set[tuple[int, int]] = set()
    origins = [(0, 0), (0, size - 7), (size - 7, 0)]
    for r0, c0 in origins:
        for dr in range(7):
            for dc in range(7):
                coords.add((r0 + dr, c0 + dc))
    return coords


def _finder_inner(size: int) -> set[tuple[int, int]]:
    """The 3x3 inner eye of each finder."""
    coords: set[tuple[int, int]] = set()
    origins = [(0, 0), (0, size - 7), (size - 7, 0)]
    for r0, c0 in origins:
        for dr in range(2, 5):
            for dc in range(2, 5):
                coords.add((r0 + dr, c0 + dc))
    return coords


def _separator_coords(size: int) -> set[tuple[int, int]]:
    coords: set[tuple[int, int]] = set()
    for i in range(8):
        # Top-left
        coords.add((7, i))
        coords.add((i, 7))
        # Top-right
        coords.add((7, size - 8 + i))
        coords.add((i, size - 8))
        # Bottom-left
        coords.add((size - 8, i))
        coords.add((size - 8 + i, 7))
    return coords


def _timing_coords(size: int) -> set[tuple[int, int]]:
    coords: set[tuple[int, int]] = set()
    for i in range(8, size - 8):
        coords.add((6, i))
        coords.add((i, 6))
    return coords


def _alignment_centers(version: int, size: int) -> list[tuple[int, int]]:
    if version < 2:
        return []
    positions = _ALIGNMENT_POSITIONS.get(version, [])
    centers: list[tuple[int, int]] = []
    for r in positions:
        for c in positions:
            # Skip if overlapping a finder pattern area
            if (r < 9 and c < 9):
                continue
            if (r < 9 and c > size - 9):
                continue
            if (r > size - 9 and c < 9):
                continue
            centers.append((r, c))
    return centers


def _alignment_regions(
    version: int, size: int
) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    outer: set[tuple[int, int]] = set()
    inner: set[tuple[int, int]] = set()
    for cr, cc in _alignment_centers(version, size):
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                coord = (cr + dr, cc + dc)
                if abs(dr) <= 1 and abs(dc) <= 1:
                    inner.add(coord)
                else:
                    outer.add(coord)
    return outer, inner


def _format_info_coords(size: int) -> set[tuple[int, int]]:
    coords: set[tuple[int, int]] = set()
    # Around top-left finder
    for i in range(9):
        coords.add((8, i))
        coords.add((i, 8))
    # Around bottom-left finder and top-right finder
    for i in range(7):
        coords.add((size - 1 - i, 8))
        coords.add((8, size - 1 - i))
    return coords


def _version_info_coords(size: int, version: int) -> set[tuple[int, int]]:
    if version < 7:
        return set()
    coords: set[tuple[int, int]] = set()
    # Bottom-left 6x3 block
    for i in range(6):
        for j in range(3):
            coords.add((size - 11 + j, i))
    # Top-right 3x6 block
    for i in range(6):
        for j in range(3):
            coords.add((i, size - 11 + j))
    return coords


def classify_matrix(matrix: list[list[bool]]) -> list[list[ModuleType]]:
    """Return a same-sized matrix of ModuleType enums."""
    size = len(matrix)
    version = _version_from_size(size)

    finder_all = _finder_regions(size)
    finder_inn = _finder_inner(size)
    separators = _separator_coords(size)
    timing = _timing_coords(size)
    align_outer, align_inner = _alignment_regions(version, size)
    fmt_info = _format_info_coords(size)
    ver_info = _version_info_coords(size, version)

    result: list[list[ModuleType]] = []
    for r in range(size):
        row: list[ModuleType] = []
        for c in range(size):
            coord = (r, c)
            if coord in finder_inn:
                mt = ModuleType.FINDER_INNER
            elif coord in finder_all:
                mt = ModuleType.FINDER_OUTER
            elif coord in separators:
                mt = ModuleType.SEPARATOR
            elif coord in align_inner:
                mt = ModuleType.ALIGNMENT_INNER
            elif coord in align_outer:
                mt = ModuleType.ALIGNMENT_OUTER
            elif coord in timing:
                mt = ModuleType.TIMING
            elif coord in fmt_info:
                mt = ModuleType.FORMAT_INFO
            elif coord in ver_info:
                mt = ModuleType.VERSION_INFO
            else:
                mt = ModuleType.DATA
            row.append(mt)
        result.append(row)
    return result
