ID = "h5py_dataset"
TITLE = "HDF5 dataset"
TAGS = ["h5py", "dataset"]
REQUIRES = ['h5py']
DISPLAY_INPUT = "h5py.File(...).create_dataset('data', data=[1, 2, 3])"
EXPECTED = "An HDF5 Dataset '/data' with shape (3,) and dtype int64. Sample: 1."


def build():
    import h5py

    file = h5py.File("in_memory.h5", "w", driver="core", backing_store=False)
    dset = file.create_dataset("data", data=[1, 2, 3])
    return dset, file
