import re

from hypothesis import given, settings, strategies as st

from house_painting_quote_parser import (
    clean_colour_name,
    room_area,
    total_wall_area,
)


@settings(max_examples=200, deadline=None)
@given(st.text() | st.none())
def test_clean_colour_name_handles_arbitrary_text(s):
    result = clean_colour_name(s)

    assert isinstance(result, str)
    if s is None:
        assert result == ""
    else:
        assert result == re.sub(r"\s+", "_", s.strip()).lower()


@settings(max_examples=200, deadline=None)
@given(st.text() | st.none())
def test_room_area_handles_arbitrary_text(s):
    result = room_area(s)

    assert type(result) is int
    assert result >= 0
    if not isinstance(s, str):
        assert result == 0
        return

    match = re.fullmatch(r"\s*([0-9]{1,9})\s*[xX]\s*([0-9]{1,9})\s*", s)
    if match is None:
        assert result == 0
        return

    length, width = (int(value) for value in match.groups())
    assert result == (length * width if length > 0 and width > 0 else 0)


@settings(max_examples=200, deadline=None)
@given(st.text() | st.none())
def test_total_wall_area_handles_arbitrary_text(s):
    result = total_wall_area(s)

    assert type(result) is int
    assert result >= 0
    if not isinstance(s, str) or not s.strip() or len(s) > 10_000:
        assert result == 0
        return

    parts = s.split(";")
    valid = len(parts) <= 1_000 and all(
        re.fullmatch(r"[0-9]{1,9}", part.strip()) for part in parts
    )
    if valid:
        assert result == sum(int(part.strip()) for part in parts)
    else:
        assert result == 0


def test_normal_examples_are_preserved():
    assert clean_colour_name("Ocean Blue") == "ocean_blue"
    assert room_area("12x10") == 120
    assert total_wall_area("120;95;110") == 325


def test_parser_handles_spacing_and_case():
    assert clean_colour_name("  Light   Blue  ") == "light_blue"
    assert room_area(" 12 X 10 ") == 120
    assert total_wall_area(" 120 ; 95 ; 110 ") == 325


def test_room_area_rejects_invalid_dimensions():
    for value in (None, "", "0x10", "-1x10", "12x", "12x3x4", "1234567890x2"):
        assert room_area(value) == 0


def test_total_wall_area_rejects_invalid_lists():
    for value in (None, "", "120;bad", "5;;3", "-1;2", "1234567890"):
        assert total_wall_area(value) == 0


def test_total_wall_area_rejects_inputs_over_safety_limits():
    assert total_wall_area("1;" * 1001 + "1") == 0
    assert total_wall_area("1" * 10_001) == 0
