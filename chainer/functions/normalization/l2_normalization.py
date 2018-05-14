import numpy

from chainer.backends import cuda
from chainer import function_node
import chainer.functions
from chainer.utils import type_check


class _WhereIndices(function_node.FunctionNode):

    def __init__(self, shape, indices):
        self.shape = shape
        self.indices = indices

    def forward(self, inputs):
        x, = inputs
        xp = cuda.get_array_module(x)
        y = xp.zeros(self.shape, x.dtype)
        y[self.indices] = x
        return y,

    def backward(self, indices, grad_outputs):
        g, = grad_outputs
        return g[self.indices],


def _where_indices(shape_and_indices, values):
    shape, indices = shape_and_indices
    out, = _WhereIndices(shape, indices).apply((values,))
    return out


class NormalizeL2(function_node.FunctionNode):

    """L2 normalization"""

    def __init__(self, eps=1e-5, axis=1):
        self.eps = eps
        self.axis = axis

    def check_type_forward(self, in_types):
        type_check.expect(in_types.size() == 1)
        x_type, = in_types

        type_check.expect(
            x_type.dtype == numpy.float32,
        )

    def forward(self, inputs):
        self.retain_inputs((0,))
        x, = inputs
        xp = cuda.get_array_module(x)
        norm = xp.linalg.norm(x, axis=self.axis, keepdims=True) + self.eps
        return x / norm,

    def backward(self, indexes, grad_outputs):
        x, = self.get_retained_inputs()
        gy, = grad_outputs
        F = chainer.functions

        norm_noeps = F.sqrt(F.sum(F.square(x), axis=self.axis, keepdims=True))
        norm = norm_noeps + self.eps
        norm = F.broadcast_to(norm, gy.shape)

        x_gy_reduced = F.sum((x * gy), axis=self.axis, keepdims=True)
        nonzero_indices = norm_noeps.array.nonzero()
        x_gy_reduced = _where_indices(
            (norm_noeps.shape, nonzero_indices),
            x_gy_reduced[nonzero_indices] / norm_noeps[nonzero_indices],
        )
        x_gy_reduced = F.broadcast_to(x_gy_reduced, gy.shape)
        gx = gy * norm - x_gy_reduced * x
        gx = gx / norm ** 2

        return gx,


def normalize(x, eps=1e-5, axis=1):
    """L2 norm squared (a.k.a.\\  Euclidean norm).

    This function implements L2 normalization on a vector along the given axis.
    No reduction is done along the normalization axis.

    In the case when :obj:`axis=1` and :math:`x` is a vector of dimension
    :math:`(N, K)`, where :math:`N` and :math:`K` denote mini-batch size and
    the dimension of the input variable, this function computes an output
    vector :math:`y` by the following equation:

    .. math::
       y_i = {x_i \\over \\| x_i \\|_2 + \\epsilon}

    :obj:`eps` is used to avoid division by zero when norm of :math:`x` along
    the given axis is zero.

    The default value of :obj:`axis` is determined for backward compatibility.

    Args:
        x (~chainer.Variable): Two dimensional output variable. The first
            dimension is assumed to be the mini-batch dimension.
        eps (float): Epsilon value for numerical stability.
        axis (int): Axis along which to normalize.

    Returns:
        ~chainer.Variable: The output variable which has the same shape
        as :math:`x`.

    """
    return NormalizeL2(eps, axis).apply((x,))[0]
