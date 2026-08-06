ID = "pydantic_adapter_nl"
TITLE = "Pydantic model"
TAGS = ["pydantic", "model"]
REQUIRES = ['pydantic']
DISPLAY_INPUT = "Employee(name='Priya Sharma', role='Senior Engineer', ...)"


def build():
    from pydantic import BaseModel

    class Employee(BaseModel):
        name: str
        role: str
        salary: float
        years: int
        skills: list[str]

    return Employee(
        name="Priya Sharma",
        role="Senior Engineer",
        salary=142500.0,
        years=6,
        skills=["python", "rust"],
    )


def expected(meta):
    object_type = meta["object_type"]
    fields = list((meta.get("fields") or {}).keys())
    values = (meta.get("metadata") or {}).get("values") or {}
    shown = fields[:8]
    pairs = ", ".join(f"{name}={values.get(name)!r}" for name in shown)
    suffix = f", ... ({len(fields)} fields total)" if len(fields) > 8 else ""
    if not pairs:
        return f"A Pydantic model {object_type}."
    return f"A Pydantic model {object_type} with fields: {pairs}{suffix}."
