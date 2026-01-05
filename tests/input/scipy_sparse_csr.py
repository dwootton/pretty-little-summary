ID = "scipy_sparse_csr"
TITLE = "SciPy CSR matrix"
TAGS = ["scipy", "sparse"]
REQUIRES = ['scipy']
DISPLAY_INPUT = "sp.csr_matrix([[0, 1], [2, 0]])"
EXPECTED = "A csr sparse matrix with shape (2, 2)."


def build():
    from scipy import sparse as sp

    return sp.csr_matrix([[0, 1], [2, 0]])
