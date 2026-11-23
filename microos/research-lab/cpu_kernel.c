#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

/*
 * C Implementation of the CPU Burn Kernel for Multi-Core Scheduling Benchmark
 * Mirrors the exact Rust black_box logic:
 *   for i in 0..units * 1000 { x = (x * 31 + i) & 0xFFFFFFFF; }
 */
static PyObject* py_burn(PyObject* self, PyObject* args) {
    unsigned long long units;
    if (!PyArg_ParseTuple(args, "K", &units)) {
        return NULL;
    }

    uint64_t x = 0;
    uint64_t limit = units * 1000ULL;
    for (uint64_t i = 0; i < limit; i++) {
        x = (x * 31ULL + i) & 0xFFFFFFFFULL;
    }

    /* Prevent compiler dead code elimination */
    #if defined(__GNUC__) || defined(__clang__)
        __asm__ __volatile__("" : "+r"(x));
    #endif

    return PyLong_FromUnsignedLongLong(x);
}

static PyMethodDef KernelMethods[] = {
    {"burn", py_burn, METH_VARARGS, "Execute CPU burn units"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef kernelmodule = {
    PyModuleDef_HEAD_INIT,
    "cpu_kernel",
    "MicroOS C CPU Burn Kernel Extension",
    -1,
    KernelMethods
};

PyMODINIT_FUNC PyInit_cpu_kernel(void) {
    return PyModule_Create(&kernelmodule);
}
