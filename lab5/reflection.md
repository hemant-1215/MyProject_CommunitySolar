# Lab 5 - Reflection

## 1. Which tools were most helpful, and why?
Bandit was the most useful for security because it points at specific risky lines (hardcoded secret, `random`, `assert`, Mako). Pylint gave the biggest quality gain (score went from 4.43 to 10.00) by pushing naming, docstrings and clean idioms. Flake8 was quick to fix and kept the file consistent with PEP 8.

## 2. Were there false positives or things the tools missed?
The tools missed several real problems: AES-ECB mode, XML parsing without XXE protection, non-constant-time signature comparison, a 150% coupon, the off-by-one trial check, the December crash in the billing date, the retry loop running 4 times, and the refund ignoring days used. I found these by reading the code and the demo output. Static analysis only catches known patterns; it cannot know what the business rules should be.

## 3. How did you decide what to fix first?
Security first (Bandit), then correctness and quality (Pylint), then formatting (Flake8), because secrets and injection bugs have the highest impact while style issues have none on behaviour. I made one commit per tool so each step can be reviewed and reverted separately.

## 4. How does static analysis help code quality and maintainability?
It gives an objective, repeatable review before the code runs. It catches cheap mistakes early, enforces a shared style, and documents risks. It works best combined with tests and code review, and best when run automatically (for example in CI) rather than once at the end.
