ID = "json_string"
TITLE = "JSON string"
TAGS = ["text", "json"]
DISPLAY_INPUT = '{"user": {"name": "alice", ...}, "active": true, "last_login": "..."}'
EXPECTED = "A valid JSON string containing an object with keys: user, active, last_login."


def build():
    import json

    payload = {
        "user": {"name": "alice", "age": 30, "roles": ["admin", "editor"]},
        "active": True,
        "last_login": "2026-07-30T12:00:00Z",
    }
    return json.dumps(payload)
