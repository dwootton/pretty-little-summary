ID = "attrs_adapter"
TITLE = "Attrs class"
TAGS = ["attrs", "dataclass"]
REQUIRES = ['attr']
DISPLAY_INPUT = "Employee('Priya Sharma', 'Senior Engineer', 142500.0, ...)"
EXPECTED = (
    "An attrs class Employee with attributes: name='Priya Sharma', "
    "role='Senior Engineer', salary=142500.0, department='Platform', years=6."
)


def build():
    import attr

    @attr.define
    class Employee:
        name: str
        role: str
        salary: float
        department: str
        years: int

    return Employee("Priya Sharma", "Senior Engineer", 142500.0, "Platform", 6)
