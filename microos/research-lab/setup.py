from setuptools import setup, Extension

module = Extension("cpu_kernel", sources=["cpu_kernel.c"])

setup(
    name="cpu_kernel",
    version="0.1.0",
    description="MicroOS Multi-Core Scheduling CPU Kernel",
    author="Tadigotla Vasanth Diwakar",
    ext_modules=[module]
)
