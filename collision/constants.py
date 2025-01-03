from enum import Enum, auto


class FieldTypes(Enum):
    """
    Store some named integer values.
    auto() function gives each constant of the class
    a unique integer value automatically.

    """

    string = auto()
    string_list = auto()
    short_string_list = auto()
    iso_date_string = auto()
    long_string = auto()
    decimal = auto()
    integer = auto()
    boolean = auto()
