# Lab 7 — Fuzzing for Input Validation Bugs

This lab hardens the provided house-painting input parser. Hypothesis generates ordinary, malformed, empty, Unicode, and null inputs to check that the parser functions return safely instead of crashing.

## Files

- \`house_painting_quote_parser.py\`: validated parser functions and a small interactive demonstration.
- \`test_house_painting_quote_parser.py\`: three property-based Hypothesis tests plus representative valid-input examples.
- \`requirements.txt\`: pytest and Hypothesis dependencies.

## Safe-input behavior

- \`clean_colour_name(value)\` returns a lowercase, underscore-separated name. Repeated whitespace is normalized. Non-string values return an empty string.
- \`room_area(value)\` accepts positive whole-foot dimensions such as \`12x10\` or \`12 X 10\` and returns their product. Malformed, non-positive, non-string, or oversized dimensions return \`0\`.
- \`total_wall_area(value)\` accepts semicolon-separated non-negative whole-foot areas such as \`120; 95; 110\`. If any token is malformed, or the input exceeds the parser's limits, it returns \`0\`.

Returning safe fallback values keeps malformed user input from terminating the program. The interactive demo uses these same functions.

## Bugs found and fixes

- \`clean_colour_name\` crashed on \`None\` and treated tabs or repeated whitespace inconsistently. It now checks the input type and normalizes all whitespace.
- \`room_area\` crashed for missing separators, extra separators, non-numeric dimensions, and \`None\`. It now validates the complete dimension string before converting it.
- \`total_wall_area\` crashed for empty input, \`None\`, or a non-numeric wall segment. It now validates the complete list and returns a safe fallback if any part is invalid.

## Run the tests

From this folder:

\`\`\`sh
python -m pip install -r requirements.txt
python -m pytest
\`\`\`

Hypothesis runs 200 generated examples for each parser property test. To try the interactive demonstration:

\`\`\`sh
python house_painting_quote_parser.py
\`\`\`
