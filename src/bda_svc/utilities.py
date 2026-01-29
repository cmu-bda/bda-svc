"""A collection of utility functions."""

import torch
import transformers


def test_gpu() -> None:
    """Verify hardware acceleration and library versions."""
    print(f"Transformers Version: {transformers.__version__}")
    print(f"PyTorch Version: {torch.__version__}")

    cuda_available = torch.cuda.is_available()
    if cuda_available:
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"Device: {torch.cuda.get_device_name()}")
    else:
        print("WARNING: CUDA not found.")
