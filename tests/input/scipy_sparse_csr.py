ID = "scipy_sparse_csr"
TITLE = "SciPy CSR matrix"
TAGS = ["scipy", "sparse"]
REQUIRES = ['scipy']
DISPLAY_INPUT = "sp.csr_matrix(([1,2,3,4,5,6], ([0,1,2,3,4,5], [1,3,0,5,2,4])), shape=(6, 6))"
EXPECTED = "A csr sparse matrix with shape (6, 6), 6 non-zero values (16.7% density)."


def build():
    from scipy import sparse as sp

    data = [1, 2, 3, 4, 5, 6]
    rows = [0, 1, 2, 3, 4, 5]
    cols = [1, 3, 0, 5, 2, 4]
    return sp.csr_matrix((data, (rows, cols)), shape=(6, 6))
