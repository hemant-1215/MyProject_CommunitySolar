# Lab 6 — House Painting Quote

This lab completes the house-painting quote module with automated tests for its normal cases, boundary conditions, and error paths.

## Files

- `house_painting_quote.py`: quote, paint-quantity, and crew-duration functions from the provided assignment.
- `test_house_painting_quote.py`: pytest tests covering valid inputs, threshold boundaries, and each validation/error branch.
- `pytest.ini`: enables statement and branch coverage, and fails the run if coverage is below 100%.
- `requirements.txt`: test and coverage tools.

## Rules implemented by the provided module

### Quote

- Supported paints are distemper (₹12/sq ft/coat), emulsion (₹20), and enamel (₹30).
- Area must be positive and coats must be at least one.
- Distemper is not allowed for exterior work; exterior quotes add ₹5 per sq ft.
- Areas above 2,000 sq ft receive a 10% discount.
- The minimum quote is ₹5,000.

### Paint quantity

- Smooth surfaces cover 100 sq ft per litre; rough surfaces cover 60 sq ft per litre.
- Paint is rounded up to whole litres.
- Other surface labels raise `ValueError`.

### Crew duration

- A painter covers 400 sq ft per day.
- The work duration is rounded up to whole days.
- Wallpaper removal adds two days.
- At least one painter is required.

## Run

From this folder:

```sh
python -m pip install -r requirements.txt
python -m pytest
```

The pytest configuration enables branch coverage and requires 100% coverage of `house_painting_quote.py`. A successful run prints the measured coverage percentage and missing-line report (which should be empty).
