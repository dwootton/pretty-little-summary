"""Basic demonstration of pretty_little_summary functionality."""

import pretty_little_summary as pls

# Example 1: Simple dictionary (GenericAdapter)
data = {"name": "Alice", "age": 30, "city": "San Francisco"}

print("=" * 60)
print("Example 1: Dictionary (GenericAdapter)")
print("=" * 60)

# Deterministic mode (no LLM call needed)
result = pls.describe(data, explain=False)

print(f"\nContent: {result.content}")
print(f"\nMetadata:")
print(f"  Object Type: {result.meta['object_type']}")
print(f"  Adapter Used: {result.meta['adapter_used']}")
print(f"\nHistory: {result.history}")

# Example 2: List
numbers = [1, 2, 3, 4, 5]

print("\n" + "=" * 60)
print("Example 2: List (GenericAdapter)")
print("=" * 60)

result = pls.describe(numbers, explain=False)

print(f"\nContent: {result.content}")
print(f"\nMetadata:")
print(f"  Object Type: {result.meta['object_type']}")
print(f"  Raw Repr: {result.meta.get('raw_repr', 'N/A')[:50]}")

# Example 3: Custom class
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.email = f"{name.lower()}@example.com"

    def greet(self):
        return f"Hello, I'm {self.name}"

person = Person("Bob", 25)

print("\n" + "=" * 60)
print("Example 3: Custom Class (GenericAdapter)")
print("=" * 60)

result = pls.describe(person, explain=False)

print(f"\nContent: {result.content}")
print(f"\nMetadata:")
print(f"  Object Type: {result.meta['object_type']}")
print(f"  Attributes: {result.meta.get('metadata', {}).get('attributes', [])[:10]}")

print("\n" + "=" * 60)
print("All examples completed successfully!")
print("=" * 60)
print("\nTo use LLM mode (explain=True), you need to:")
print("1. Set OPENROUTER_API_KEY environment variable, or")
print("2. Call pls.configure(openrouter_api_key='sk-or-...')")
print("\nThen run: result = pls.describe(obj, explain=True)")
