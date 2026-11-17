import pytest

from house_painting_quote import crew_days, paint_litres, painting_quote


@pytest.mark.parametrize(
    ("paint", "area", "coats", "expected"),
    [
        ("distemper", 100, 2, 5000),  # Minimum quote applies.
        ("emulsion", 300, 1, 6000),  # Above the minimum.
        ("enamel", 500, 2, 30000),   # Upper paint-rate option.
    ],
)
def test_interior_quote_by_paint_rate(paint, area, coats, expected):
    assert painting_quote(paint, area, coats, False) == expected


def test_exterior_enamel_adds_exterior_rate():
    # Existing starter example: (500 * 30 * 2) + (500 * 5)
    assert painting_quote("enamel", 500, 2, True) == 32500


def test_large_job_receives_ten_percent_discount():
    # 2,001 * ₹20 = ₹40,020; the integer 10% discount is ₹4,002.
    assert painting_quote("emulsion", 2001, 1, False) == 36018


@pytest.mark.parametrize(
    ("paint", "area", "coats", "is_exterior", "message"),
    [
        ("primer", 300, 1, False, "unknown paint"),
        ("distemper", 300, 1, True, "interiors only"),
    ],
)
def test_invalid_paint_or_exterior_distemper_raises(
    paint, area, coats, is_exterior, message
):
    with pytest.raises(ValueError, match=message):
        painting_quote(paint, area, coats, is_exterior)


@pytest.mark.parametrize(
    ("area", "coats"),
    [
        (0, 1),   # Short-circuits at the non-positive area check.
        (-1, 1),  # Negative area is also invalid.
        (100, 0), # Positive area reaches and fails the coat-count check.
    ],
)
def test_invalid_job_dimensions_raise(area, coats):
    with pytest.raises(ValueError, match="invalid job"):
        painting_quote("emulsion", area, coats, False)


def test_smooth_litres_for_exact_coverage():
    assert paint_litres(200, 1, "smooth") == 2


def test_smooth_litres_round_up_for_partial_coverage():
    assert paint_litres(201, 1, "smooth") == 3


def test_rough_litres_for_exact_coverage():
    assert paint_litres(120, 1, "rough") == 2


def test_rough_litres_round_up_for_partial_coverage():
    assert paint_litres(121, 1, "rough") == 3


def test_unknown_surface_raises():
    with pytest.raises(ValueError, match="unknown surface"):
        paint_litres(100, 1, "textured")


def test_crew_days_for_exact_daily_capacity():
    assert crew_days(800, 2, False) == 1


def test_crew_days_round_up_for_partial_day():
    assert crew_days(801, 2, False) == 2


def test_crew_days_add_two_days_for_wallpaper_removal():
    assert crew_days(1, 1, True) == 3


@pytest.mark.parametrize("painters", [0, -1])
def test_crew_requires_at_least_one_painter(painters):
    with pytest.raises(ValueError, match="at least one painter"):
        crew_days(400, painters, False)
