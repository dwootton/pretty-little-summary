"""Live library objects exercising the optional-dependency adapters.

All builders use fixed seeds so metadata (and goldens) stay deterministic.
"""

from __future__ import annotations

from evals.cases import CaseCtx, case


@case(
    "live/sklearn_fitted_rf",
    tags=("adapter", "sklearn", "ml"),
    requires=("sklearn", "numpy"),
    display_input="RandomForestClassifier(n_estimators=10) fit on 100x4 random data",
    notes="Should report fitted status, estimator type, and key hyperparameters.",
)
def fitted_rf(ctx: CaseCtx):
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier

    rng = np.random.default_rng(0)
    X, y = rng.random((100, 4)), rng.integers(0, 2, 100)
    return RandomForestClassifier(n_estimators=10, random_state=0).fit(X, y)


@case(
    "live/sklearn_unfitted",
    tags=("adapter", "sklearn", "ml"),
    requires=("sklearn",),
    display_input="LogisticRegression() never fitted",
    notes="Should say it is NOT fitted — the crucial fact about this object.",
)
def unfitted_lr(ctx: CaseCtx):
    from sklearn.linear_model import LogisticRegression

    return LogisticRegression(max_iter=200)


@case(
    "live/sklearn_pipeline",
    tags=("adapter", "sklearn", "ml"),
    requires=("sklearn", "numpy"),
    display_input="Pipeline(StandardScaler -> PCA(3) -> Ridge) fit on 50x8 data",
    notes="Should name the steps in order; a pipeline is defined by its stages.",
)
def sk_pipeline(ctx: CaseCtx):
    import numpy as np
    from sklearn.decomposition import PCA
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    rng = np.random.default_rng(2)
    pipe = Pipeline(
        [("scale", StandardScaler()), ("pca", PCA(n_components=3)), ("model", Ridge())]
    )
    return pipe.fit(rng.random((50, 8)), rng.random(50))


@case(
    "live/mpl_subplots",
    tags=("adapter", "matplotlib", "viz"),
    requires=("matplotlib",),
    display_input="2x2 matplotlib subplots: histogram, line, scatter, empty",
    notes="Should describe the grid and per-axes chart types.",
)
def mpl_fig(ctx: CaseCtx):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2)
    axes[0][0].hist([1, 2, 2, 3, 3, 3])
    axes[0][0].set_title("hist")
    axes[0][1].plot([0, 1, 2], [0, 1, 4])
    axes[1][0].scatter([1, 2, 3], [3, 1, 2])
    return fig, lambda: plt.close(fig)


@case(
    "live/torch_tensor_3d",
    tags=("adapter", "torch", "ml"),
    requires=("torch",),
    display_input="float32 torch tensor of shape (8, 3, 224) from manual_seed(0)",
    notes="Should report shape, dtype, device; basic stats are a plus.",
)
def torch_tensor(ctx: CaseCtx):
    import torch

    torch.manual_seed(0)
    return torch.rand(8, 3, 224)


@case(
    "live/networkx_karate",
    tags=("adapter", "networkx", "graph"),
    requires=("networkx",),
    display_input="networkx karate club graph (34 nodes, 78 edges)",
    notes="Should report node/edge counts and that it is undirected.",
)
def karate(ctx: CaseCtx):
    import networkx as nx

    return nx.karate_club_graph()


@case(
    "live/pydantic_model_instance",
    tags=("adapter", "pydantic", "structured"),
    requires=("pydantic",),
    display_input="Pydantic User model instance with nested Address",
    notes="Should show the field names/types, i.e. the schema plus the values.",
)
def pydantic_user(ctx: CaseCtx):
    from pydantic import BaseModel

    class Address(BaseModel):
        city: str
        zip_code: str

    class User(BaseModel):
        name: str
        age: int
        address: Address
        tags: list[str] = []

    return User(
        name="Ada",
        age=36,
        address=Address(city="London", zip_code="EC1"),
        tags=["math", "computing"],
    )


@case(
    "live/polars_lazyframe",
    tags=("adapter", "polars", "data"),
    requires=("polars",),
    display_input="polars LazyFrame with a filter+groupby plan over 1000 rows",
    notes="Should make clear it is lazy/unevaluated, ideally sketching the plan.",
)
def pl_lazy(ctx: CaseCtx):
    import polars as pl

    df = pl.DataFrame(
        {"g": [i % 5 for i in range(1000)], "v": [float(i) for i in range(1000)]}
    )
    return df.lazy().filter(pl.col("v") > 100).group_by("g").agg(pl.col("v").mean())


@case(
    "live/pil_gradient_image",
    tags=("adapter", "pil", "viz"),
    requires=("PIL",),
    display_input="PIL RGB image 320x200 with a computed gradient",
    notes="Should report mode and dimensions.",
)
def pil_image(ctx: CaseCtx):
    from PIL import Image

    img = Image.new("RGB", (320, 200))
    img.putdata(
        [(x % 256, y % 256, (x + y) % 256) for y in range(200) for x in range(320)]
    )
    return img


@case(
    "live/scipy_sparse_csr",
    tags=("adapter", "scipy", "data"),
    requires=("scipy", "numpy"),
    display_input="scipy CSR matrix 1000x1000 with ~1% density, seed 3",
    notes="Should report shape, nnz/density, and format — not densify.",
)
def sparse_csr(ctx: CaseCtx):
    import numpy as np
    from scipy import sparse

    rng = np.random.default_rng(3)
    return sparse.random(1000, 1000, density=0.01, format="csr", random_state=rng)


@case(
    "live/xarray_dataset",
    tags=("adapter", "xarray", "science"),
    requires=("xarray", "numpy"),
    display_input="xarray Dataset with temp(time=48, lat=5, lon=5) and units attr",
    notes="Should name dims/coords and data variables.",
)
def xr_dataset(ctx: CaseCtx):
    import numpy as np
    import xarray as xr

    rng = np.random.default_rng(4)
    return xr.Dataset(
        {"temp": (("time", "lat", "lon"), rng.normal(15, 3, (48, 5, 5)))},
        coords={
            "time": np.arange(48),
            "lat": np.linspace(-10, 10, 5),
            "lon": np.linspace(0, 20, 5),
        },
        attrs={"units": "degC"},
    )


@case(
    "live/generator_object",
    tags=("adapter", "stdlib", "edge"),
    display_input="a generator expression (x*x for x in range(1000)), unconsumed",
    notes="Must NOT consume the generator; should say it is lazy/unconsumed.",
)
def generator_obj(ctx: CaseCtx):
    return (x * x for x in range(1000))
