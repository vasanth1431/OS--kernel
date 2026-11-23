// Listing 2: Rust CPU Kernel for Multi-Core Scheduling Benchmark
// PyO3 native acceleration module for MicroOS Research Lab
// Author: Tadigotla Vasanth Diwakar (USN: 25BTRCL270)

use pyo3::prelude::*;
use std::hint::black_box;

#[pyfunction]
fn burn(units: u64) -> u64 {
    let mut x: u64 = 0;
    for i in 0..units * 1000 {
        x = x.wrapping_mul(31).wrapping_add(i) & 0xFFFF_FFFF;
    }
    black_box(x)
}

#[pymodule]
fn cpu_kernel(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(burn, m)?)?;
    Ok(())
}
