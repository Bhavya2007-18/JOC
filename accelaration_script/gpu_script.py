import torch
import time

device = "cuda" if torch.cuda.is_available() else "cpu"

try:
    while True:
        # Create big tensors
        a = torch.randn(3000, 3000, device=device)
        b = torch.randn(3000, 3000, device=device)

        # Heavy computation
        c = torch.matmul(a, b)

        # Keep GPU timing accurate only when running on CUDA.
        if device == "cuda":
            torch.cuda.synchronize()

        # Small pause to avoid pegging the host at 100%.
        time.sleep(0.01)
except KeyboardInterrupt:
    pass
    