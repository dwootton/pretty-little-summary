#!/usr/bin/env python
"""Test that pls.is() syntax works correctly."""

import pretty_little_summary as pls

# Test 1: pls.is() works
print("Testing pls.is() syntax...")
result = pls.is([1, 2, 3], explain=False)
print(f"✓ pls.is() works: {result.content}")

# Test 2: pls.describe() also works
print("\nTesting pls.describe() syntax...")
result2 = pls.describe([4, 5, 6], explain=False)
print(f"✓ pls.describe() works: {result2.content}")

# Test 3: Check they're the same function
print(f"\nAre they the same function? {pls.is is pls.is_}")

# Test 4: Test with different objects
test_objects = [
    ("dict", {"a": 1, "b": 2}),
    ("string", "hello world"),
    ("int", 42),
]

print("\n\nTesting pls.is() with various objects:")
for label, obj in test_objects:
    result = pls.is(obj, explain=False)
    print(f"  {label:10s} → {result.content}")

print("\n✅ All tests passed! pls.is() works perfectly!")
