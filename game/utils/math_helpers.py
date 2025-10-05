"""
utils/math_helpers.py
=====================
Simple math utilities/helpers.
"""


def clamp(value, min_value, max_value):
    """Clamp a value between `min_value` and `max_value`."""
    return max(min_value, min(value, max_value))


def scale_to_index(ratio: float, size: int) -> int:
    """Scale a 0-1 `ratio` to an integer index in range [0, size-1]."""
    return int(round(ratio * (size - 1)))


def normalize(value: float, min_value: float, max_value: float) -> float:
    """Normalize `value` to range [0,1] with given `min_value` and `max_value` bounds."""
    return (value - min_value) / (max_value - min_value)
