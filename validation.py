"""Date of birth and age validation."""

from datetime import date, datetime


class DOBValidationError(Exception):
    """Raised when date of birth is invalid or in the future."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def _age_years(dob: date, ref: date) -> int:
    """Calculate age in completed years."""
    age = ref.year - dob.year
    if (ref.month, ref.day) < (dob.month, dob.day):
        age -= 1
    return age


def validate_dob(
    value: str,
    min_age: int | None = None,
    reference_date: date | None = None,
) -> date:
    """
    Validate date of birth: YYYY-MM-DD format, not in future.
    If min_age is set, age must be greater than min_age (e.g. min_age=18 means age > 18).
    Raises DOBValidationError on failure.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise DOBValidationError("Date of birth cannot be empty.")

    s = str(value).strip()
    try:
        dob = datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise DOBValidationError(
            "Date of birth must be in format YYYY-MM-DD (e.g. 2015-03-20)."
        )

    ref = reference_date or date.today()
    if dob > ref:
        raise DOBValidationError("Date of birth cannot be in the future.")

    if min_age is not None:
        age = _age_years(dob, ref)
        if age <= min_age:
            raise DOBValidationError(
                f"Age must be greater than {min_age} years (current age: {age})."
            )
    return dob
