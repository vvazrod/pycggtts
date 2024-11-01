# pycggtts

Python package to perform remote clock comparison using CGGTTS files.

## Installation

```bash
pip install pycggtts
```

## Usage

```python
from pycggtts import CGGTTS

cggtts = CGGTTS.from_file("path/to/cggtts/file")

# You can now access file and track data
print(cggtts.station)
print(cggtts.tracks[0].refsys)
```

## Notes

This package is basically a Python re-implementation of the
[gwbres/cggtts](https://github.com/gwbres/cggtts) Rust crate. The purpose of this
package is to allow users to work with CGGTTS data in environments where Python is a
more natural choice than Rust (data visualization, machine learning, etc.). Thus, it
currently only supports reading from files and not writing CGGTTS-compliant files.

Please note that this package is still in its early stages and may contain bugs and
other unsupported features. If you encounter any issues, please open an issue on the
[GitHub repository](https://github.com/vvazrod/pycggtts).
