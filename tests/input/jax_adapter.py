ID = "jax_adapter"
TITLE = "JAX array"
TAGS = ["jax", "array"]
REQUIRES = ['jax']
DISPLAY_INPUT = "jnp.array([1, 2, 3])"
EXPECTED = "A JAX array with shape (3,)."


def build():
    import jax.numpy as jnp

    return jnp.array([1, 2, 3])
