ID = "pydantic_adapter_nl"
TITLE = "Pydantic model"
TAGS = ["pydantic", "model"]
REQUIRES = ['pydantic']
DISPLAY_INPUT = "User(name='alice', age=30)"


def build():
    from pydantic import BaseModel

    class User(BaseModel):
        name: str
        age: int

    return User(name="alice", age=30)


def expected(meta):
    return f"A Pydantic model {meta['object_type']}."
