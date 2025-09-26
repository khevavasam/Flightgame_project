def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def scale_to_index(ratio: float, size: int) -> int:
    return int(round(ratio * (size - 1)))


def normalize(value: float, min_value: float, max_value: float) -> float:
    return (value - min_value) / (max_value - min_value)
