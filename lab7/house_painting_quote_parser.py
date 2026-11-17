"""Input-safe parsers for house-painting quote details."""


import re


_COLOUR_WHITESPACE = re.compile(r"\s+")
_ROOM_SIZE = re.compile(r"\s*([0-9]{1,9})\s*[xX]\s*([0-9]{1,9})\s*")
_WALL_AREA = re.compile(r"[0-9]{1,9}")


def clean_colour_name(name):
    """Normalize a colour name; return an empty string for non-text input."""
    if not isinstance(name, str):
        return ""

    return _COLOUR_WHITESPACE.sub("_", name.strip()).lower()


def room_area(text):
    """Parse positive LENGTHxWIDTH dimensions, returning 0 if invalid."""
    if not isinstance(text, str):
        return 0

    match = _ROOM_SIZE.fullmatch(text)
    if match is None:
        return 0

    length, width = (int(value) for value in match.groups())
    if length <= 0 or width <= 0:
        return 0

    return length * width


def total_wall_area(text):
    """Sum semicolon-separated whole-number areas; invalid lists return 0."""
    if not isinstance(text, str) or not text.strip() or len(text) > 10_000:
        return 0

    parts = text.split(";")
    if len(parts) > 1_000:
        return 0

    areas = []
    for part in parts:
        token = part.strip()
        if _WALL_AREA.fullmatch(token) is None:
            return 0
        areas.append(int(token))

    return sum(areas)


def main():
    print("==== Running clean_colour_name ====")
    value = input("Enter a paint colour name (e.g. Ocean Blue): ")
    print("Colour code:", clean_colour_name(value))

    print("\n==== Running room_area ====")
    value = input("Enter room size as LENGTHxWIDTH in feet (e.g. 12x10): ")
    print("Room area (sq ft):", room_area(value))

    print("\n==== Running total_wall_area ====")
    value = input("Enter wall areas separated by ; (e.g. 120;95;110): ")
    print("Total wall area (sq ft):", total_wall_area(value))


if __name__ == "__main__":
    main()
