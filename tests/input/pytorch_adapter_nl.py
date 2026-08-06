ID = "pytorch_adapter_nl"
TITLE = "PyTorch tensor"
TAGS = ["pytorch", "tensor"]
REQUIRES = ['torch']
DISPLAY_INPUT = "torch.arange(12, dtype=torch.float32).reshape(3, 4)"


def build():
    import torch as t

    return t.arange(12, dtype=t.float32).reshape(3, 4)


def expected(meta):
    metadata = meta["metadata"]
    grad_str = " (requires_grad)" if metadata.get("requires_grad") else ""
    return (
        f"A PyTorch tensor with shape {metadata['shape']} and dtype "
        f"{metadata['dtype']} on {metadata['device']}{grad_str}."
    )
