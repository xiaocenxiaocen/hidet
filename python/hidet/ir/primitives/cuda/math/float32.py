# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from hidet.ir.expr import Expr
from hidet.ir.type import FuncType, func_type
from hidet.ir.dtypes import float32, float32x2, float32x4
from hidet.ir.primitives.func import register_primitive_function, primitive_func_pool
from hidet.ir.primitives.math import MathFunctionSet, register_math_function_set


class CUDAFloat32MathFunctionSet(MathFunctionSet):
    # pylint: disable=abstract-method
    @staticmethod
    def register():
        unary_funcs = {
            'sin': 'sinf',
            'cos': 'cosf',
            'tan': 'tanf',
            'sinh': 'sinhf',
            'cosh': 'coshf',
            'tanh': 'tanhf',
            'asin': 'asinf',
            'acos': 'acosf',
            'atan': 'atanf',
            'asinh': 'asinhf',
            'acosh': 'acoshf',
            'atanh': 'atanhf',
            'exp': '__expf',  # fast math
            'exp2': 'exp2f',
            'erf': 'erff',
            'sqrt': 'sqrtf',
            'rsqrt': 'rsqrtf',
            'log': 'logf',
            'round': 'roundf',
            'abs': 'fabsf',
            'ceil': 'ceilf',
            'floor': 'floorf',
            'expm1': 'expm1f',
            'log2': 'log2f',
            'log10': 'log10f',
            'log1p': 'log1pf',
            'trunc': 'truncf',
            'isfinite': 'isfinite',
            'isinf': 'isinf',
            'isnan': 'isnan',
        }
        binary_funcs = {'min': 'fminf', 'max': 'fmaxf', 'pow': 'powf', 'mod': 'fmodf', 'atan2': 'atan2f'}
        ternary_funcs = {'fma': 'fmaf'}

        for name_map, num_args in zip([unary_funcs, binary_funcs, ternary_funcs], [1, 2, 3]):
            for name, codegen_name in name_map.items():
                register_primitive_function(
                    name='cuda_f32_{}'.format(name),
                    codegen_name=codegen_name,
                    func_or_type=FuncType(
                        param_types=['float32'] * num_args,
                        ret_type='float32' if name not in ['isfinite', 'isinf', 'isnan'] else 'bool',
                    ),
                )
        register_primitive_function(
            name='cuda_f32_make_float2',
            func_or_type=func_type([float32, float32], float32x2),
            codegen_name='make_float2',
        )
        register_primitive_function(
            name='cuda_f32_make_float4',
            func_or_type=func_type([float32, float32, float32, float32], float32x4),
            codegen_name='make_float4',
        )

    @staticmethod
    def call(name: str, *args) -> Expr:
        entry = primitive_func_pool.lookup_by_name('cuda_f32_{}'.format(name))
        return entry.var(*args)

    def make_vector(self, *items) -> Expr:
        if not isinstance(items, (list, tuple)):
            raise ValueError('float32 requires a list of items')
        items = list(items)

        if len(items) == 2:
            return self.call('make_float2', items[0], items[1])
        elif len(items) == 4:
            return self.call('make_float4', items[0], items[1], items[2], items[3])
        else:
            raise ValueError('float32 requires 2 or 4 elements')

    def sin(self, a: Expr) -> Expr:
        return self.call('sin', a)

    def cos(self, a: Expr) -> Expr:
        return self.call('cos', a)

    def tanh(self, a: Expr) -> Expr:
        return self.call('tanh', a)

    def exp(self, a: Expr) -> Expr:
        return self.call('exp', a)

    def exp2(self, a: Expr) -> Expr:
        return self.call('exp2', a)

    def erf(self, a: Expr) -> Expr:
        return self.call('erf', a)

    def sqrt(self, a: Expr) -> Expr:
        return self.call('sqrt', a)

    def rsqrt(self, a: Expr) -> Expr:
        return self.call('rsqrt', a)

    def log(self, a: Expr) -> Expr:
        return self.call('log', a)

    def round(self, a: Expr) -> Expr:
        return self.call('round', a)

    def abs(self, a: Expr) -> Expr:
        return self.call('abs', a)

    def ceil(self, a: Expr) -> Expr:
        return self.call('ceil', a)

    def floor(self, a: Expr) -> Expr:
        return self.call('floor', a)

    def tan(self, a: Expr) -> Expr:
        return self.call('tan', a)

    def sinh(self, a: Expr) -> Expr:
        return self.call('sinh', a)

    def cosh(self, a: Expr) -> Expr:
        return self.call('cosh', a)

    def asin(self, a: Expr) -> Expr:
        return self.call('asin', a)

    def acos(self, a: Expr) -> Expr:
        return self.call('acos', a)

    def atan(self, a: Expr) -> Expr:
        return self.call('atan', a)

    def asinh(self, a: Expr) -> Expr:
        return self.call('asinh', a)

    def acosh(self, a: Expr) -> Expr:
        return self.call('acosh', a)

    def atanh(self, a: Expr) -> Expr:
        return self.call('atanh', a)

    def expm1(self, a: Expr) -> Expr:
        return self.call('expm1', a)

    def log2(self, a: Expr) -> Expr:
        return self.call('log2', a)

    def log10(self, a: Expr) -> Expr:
        return self.call('log10', a)

    def log1p(self, a: Expr) -> Expr:
        return self.call('log1p', a)

    def trunc(self, a: Expr) -> Expr:
        return self.call('trunc', a)

    def isfinite(self, a: Expr) -> Expr:
        return self.call('isfinite', a)

    def isinf(self, a: Expr) -> Expr:
        return self.call('isinf', a)

    def isnan(self, a: Expr) -> Expr:
        return self.call('isnan', a)

    def min(self, a: Expr, b: Expr) -> Expr:
        return self.call('min', a, b)

    def max(self, a: Expr, b: Expr) -> Expr:
        return self.call('max', a, b)

    def pow(self, a: Expr, b: Expr) -> Expr:
        return self.call('pow', a, b)

    def mod(self, a: Expr, b: Expr) -> Expr:
        return self.call('mod', a, b)

    def atan2(self, a: Expr, b: Expr) -> Expr:
        return self.call('atan2', a, b)

    def fma(self, a: Expr, b: Expr, c: Expr) -> Expr:
        return self.call('fma', a, b, c)


cuda_f32_math_function_set = CUDAFloat32MathFunctionSet()
cuda_f32_math_function_set.register()
register_math_function_set('cuda', 'float32', cuda_f32_math_function_set)
