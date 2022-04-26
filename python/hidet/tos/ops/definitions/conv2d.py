from .utils import Tensor, normalize_stride
from .conv2d_gemm import conv2d_gemm
from .conv2d_winograd import conv2d_winograd


def conv2d(input: Tensor, weight: Tensor, padding, stride) -> Tensor:
    sx, sy = normalize_stride(stride)
    kx, ky = weight.shape[2:]
    if (sx, sy) == (1, 1) and (kx, ky) == (3, 3):
        return conv2d_winograd(input, weight, padding)
    else:
        return conv2d_gemm(input, weight, padding, stride)