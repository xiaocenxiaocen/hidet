import pytest
from hidet.ir.expr import *
from hidet.ir.dialects.compute import compute
from hidet.ir.dialects.pattern import match, AnyExpr, UnionPattern, TensorComputePattern, any_const_int, compute_pattern


def check_pairs(pairs):
    for pattern, target, expect in pairs:
        actual, msg = match(pattern, target)
        if expect is None:
            assert actual is None
        else:
            for p in expect:
                assert p in actual
                assert expect[p] is actual[p]


def test_normal_expr():
    a, b, c, d = var('a'), var('b'), var('c'), var('d')

    pairs = [
        (Add(a, b), Add(c, d), {a: c, b: d}),
        (Add(a, a), Add(c, c), {a: c}),
        (Add(a, a), Add(c, d), None),
        (Add(a, b), Add(c, c), {a: c, b: c}),
    ]
    check_pairs(pairs)


def test_any_pattern():
    a, b, c, d = var('a'), var('b'), var('c'), var('d')
    s = Add(a, b)
    m = Multiply(a, b)
    any_expr = AnyExpr()
    any_var = AnyExpr(Var)
    any_add = AnyExpr(Add)

    pairs = [
        (any_expr, s, {any_expr: s}),
        (Add(any_expr, b), Add(c, d), {any_expr: c, b: d}),
        (any_var, Add(c, d), None),
        (any_add, s, {any_add: s}),
        (any_add, m, None)
    ]
    check_pairs(pairs)


def test_union_pattern():
    a, b, c, d = var('a'), var('b'), var('c'), var('d')
    add_cd = Add(c, d)
    mul_cd = Multiply(c, d)
    union = UnionPattern([Add(a, b), Multiply(a, b), a])

    pairs = [
        (union, c, {union: c, a: c}),
        (union, add_cd, {union: add_cd, a: c, b: d}),
        (union, mul_cd, {union: mul_cd, a: c, b: d}),
        (union, Mod(c, d), None)
    ]
    check_pairs(pairs)


def test_tensor_compute():
    c1 = any_const_int()
    c2 = any_const_int()
    tc1 = compute_pattern('C', [10, 10], lambda i, j: i + j)
    tc2 = compute_pattern('E', [5, 5], lambda p, q: p + q)
    tc3 = compute_pattern('F', [10, 10], lambda p, q: p * q)
    tc4 = compute_pattern('G', [c1, c2], lambda p, q: p + q)

    tgt = compute_pattern('D', [10, 10], lambda p, q: p + q)

    pairs = [
        (tc1, tgt, {tc1.axes[0]: tgt.axes[0], tc1.axes[1]: tgt.axes[1], tc1.value: tgt.value}),
        (tc2, tgt, None),
        (tc3, tgt, None),
        (tc4, tgt, {tc4.axes[0]: tgt.axes[0], tc4.axes[1]: tgt.axes[1], tc4.value: tgt.value}),
    ]
    check_pairs(pairs)


def test_tensor_compute_pattern():
    tc1 = TensorComputePattern(rank=None, allow_dynamic_axis=True)
    tc2 = TensorComputePattern(rank=None, allow_dynamic_axis=False)
    tc3 = TensorComputePattern(rank=2, allow_dynamic_axis=True)
    tc4 = TensorComputePattern(rank=2, allow_dynamic_axis=False)

    a = scalar_var('a', 'int32')
    b = scalar_var('b', 'int32')
    c = scalar_var('c', 'int32')
    tgt1 = compute_pattern('A', [10, 10], lambda i, j: i + j)
    tgt2 = compute_pattern('B', [10, 10, 10], lambda i, j, k: i + j * k)
    tgt3 = compute_pattern('C', [a, b], lambda i, j: i + j)
    tgt4 = compute_pattern('D', [a, b, c], lambda i, j, k: i + j + k)

    pairs = [
        (tc1, tgt1, {}), (tc1, tgt2, {}), (tc1, tgt3, {}), (tc1, tgt4, {}),
        (tc2, tgt1, {}), (tc2, tgt2, {}), (tc2, tgt3, None), (tc2, tgt4, None),
        (tc3, tgt1, {}), (tc3, tgt2, None), (tc3, tgt3, {}), (tc3, tgt4, None),
        (tc4, tgt1, {}), (tc4, tgt2, None), (tc4, tgt3, None), (tc4, tgt4, None),
    ]
    check_pairs(pairs)


if __name__ == '__main__':
    pytest.main(__file__)
