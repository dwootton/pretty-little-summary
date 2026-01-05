ID = "pytorch_adapter_nl"
TITLE = "PyTorch tensor"
TAGS = ["pytorch", "tensor"]
REQUIRES = ['torch']
DISPLAY_INPUT = "torch.tensor([1.0, 2.0])"


def build():
    import torch as t

    return t.tensor([1.0, 2.0])


def expected(meta):
    return f"A PyTorch tensor with shape {meta['metadata']['shape']}."
