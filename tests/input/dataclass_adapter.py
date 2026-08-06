ID = "dataclass_adapter"
TITLE = "Dataclass"
TAGS = ["stdlib", "dataclass"]
DISPLAY_INPUT = "Employee(name='Priya Sharma', role='Senior Engineer', ...)"
EXPECTED = (
    "A dataclass Employee with fields: name='Priya Sharma', "
    "role='Senior Engineer', salary=142500.0, years=6, remote=True."
)


def build():
    from dataclasses import dataclass

    @dataclass
    class Employee:
        name: str
        role: str
        salary: float
        years: int
        remote: bool

    return Employee("Priya Sharma", "Senior Engineer", 142500.0, 6, True)
