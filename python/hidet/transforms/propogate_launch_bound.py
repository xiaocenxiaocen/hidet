"""
Propagate the launch configuration cuda_block_dim and cuda_grid_dim from cuda_kernel functions
to cuda_device functions.
"""
from typing import Optional

from hidet.ir.func import Function, IRModule
from hidet.transforms.base import Pass, FunctionPass


class PropagateLaunchBoundPass(FunctionPass):
    # currently, we only deal with the module that has a single cuda kernel
    # and leave the support for multiple cuda kernels in the future.
    # please note that propagate the launch bound would help optimize the model,
    # but has no influence on the correctness.
    def __init__(self):
        super().__init__()
        self.kernel_function: Optional[Function] = None

    def process_module(self, ir_module: IRModule) -> IRModule:
        kernel_function = None
        for func in ir_module.functions.values():
            if func.kind == 'cuda_kernel':
                if kernel_function is not None:
                    return ir_module
                kernel_function = func
        if kernel_function is None:
            return ir_module
        self.kernel_function = kernel_function
        return FunctionPass.process_module(self, ir_module)

    def process_func(self, func: Function) -> Function:
        if func.kind == 'cuda_device':
            attrs = func.attrs.copy()
            attrs['cuda_block_dim'] = self.kernel_function.attrs['cuda_block_dim']
            attrs['cuda_grid_dim'] = self.kernel_function.attrs['cuda_grid_dim']
            func = Function(
                name=func.name,
                params=func.params,
                body=func.body,
                ret_type=func.ret_type,
                kind=func.kind,
                extern_vars=func.extern_vars,
                attrs=attrs,
            )
        return func


def propagate_launch_bound_pass() -> Pass:
    return PropagateLaunchBoundPass()
