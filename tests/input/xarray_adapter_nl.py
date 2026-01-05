ID = "xarray_adapter_nl"
TITLE = "Xarray DataArray"
TAGS = ["xarray", "array"]
REQUIRES = ['xarray']
DISPLAY_INPUT = "xr.DataArray([[1, 2], [3, 4]], dims=['x', 'y'])"


def build():
    import xarray as xr

    return xr.DataArray([[1, 2], [3, 4]], dims=["x", "y"])


def expected(meta):
    return (
        f"An xarray object {meta['object_type']} with shape {meta.get('shape')}. "
        "Sample: [1, 2, 3, 4]."
    )
