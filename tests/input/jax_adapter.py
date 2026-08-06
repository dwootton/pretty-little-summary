ID = "jax_adapter"
TITLE = "JAX array"
TAGS = ["jax", "array"]
REQUIRES = ['jax']
DISPLAY_INPUT = "jnp.array(np.round(np.linspace(0, 1, 12), 3))"
EXPECTED = "A JAX array with shape (12,) and dtype float32."


def build():
    import numpy as np
    import jax.numpy as jnp

    return jnp.array(np.round(np.linspace(0, 1, 12), 3))
