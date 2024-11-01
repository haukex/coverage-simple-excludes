#!/usr/bin/env python
import os
import re
import sys
from pathlib import Path
from igbpyutils.error import init_handlers
import coverage

# This test checks to make sure that all lines in test_excludes.py
# are actually covered / excluded as defined by the comments.

EXP_ALWAYS :set[str] = {
    'import os',
    'import sys',
    'import unittest',
    'class ExcludesTestCase(unittest.TestCase):',
    'def test_excludes(self):',
    'stuff :set[str] = set()',
    'empty :list = []',
    'if empty:',
    "if os.name == 'nt':",
    "if os.name == 'posix':",
    "if sys.platform == 'linux':",
    "if sys.platform == 'win32':",
    "if sys.platform != 'win32':",
    "if sys.platform == 'darwin':",
    "if sys.implementation.name == 'cpython':",
    "if sys.hexversion >= 0x03_0B_00_00:",
    "if sys.hexversion < 0x03_0C_00_00:",
    "if sys.version_info.major >= 2:",
    "if sys.version_info.major < 4:",
    "self.assertEqual(len(stuff), 11)",
}

_CMT_RE = re.compile(r'#.*?\Z')

def _get_exp():
    exp = set(EXP_ALWAYS)
    exp.add( "stuff.add('is-nt')" if os.name == 'nt' else "stuff.add('not-nt')" )
    exp.add( "stuff.add('is-posix')" if os.name == 'posix' else "stuff.add('not-posix')" )
    exp.add( "stuff.add('is-linux')" if sys.platform == 'linux' else "stuff.add('not-linux')" )
    exp.add( "stuff.add('is-win32-1')" if sys.platform == 'win32' else "stuff.add('not-win32-1')" )
    exp.add( "stuff.add('not-win32-2')" if sys.platform != 'win32' else "stuff.add('is-win32-2')" )
    exp.add( "stuff.add('is-darwin')" if sys.platform == 'darwin' else "stuff.add('not-darwin')" )
    exp.add( "stuff.add('is-cpython')" if sys.implementation.name == 'cpython' else "stuff.add('not-cpython')" )
    exp.add( "stuff.add('ge3.11')" if sys.hexversion >= 0x03_0B_00_00 else "stuff.add('lt3.11')" )
    exp.add( "stuff.add('lt3.12')" if sys.hexversion < 0x03_0C_00_00 else "stuff.add('ge3.12')" )
    exp.add( "stuff.add('ge2.0')" if sys.version_info.major>=2 else "stuff.add('lt2.0')" )
    exp.add( "stuff.add('lt4.0')" if sys.version_info.major<4 else "stuff.add('ge4.0')" )
    return exp

BASE = Path(__file__).parent.parent

def main():
    init_handlers()
    sys.path.append(str(BASE))
    cov = coverage.Coverage(
        config_file=BASE/'pyproject.toml',
        data_file=BASE/'.coverage',
    )
    cov.load()
    #cov.report(file=sys.stdout)
    data = cov.get_data()
    uut = BASE/'tests'/'test_excludes.py'
    line_nrs = data.lines(str(uut))
    assert line_nrs
    with uut.open(encoding='UTF-8') as fh:
        lines = tuple(fh)
    covered = { _CMT_RE.sub('', lines[li-1].strip()).strip() for li in line_nrs }
    expect = _get_exp()
    if covered - expect:
        raise ValueError(f"Unexpected extra line(s) covered in {uut.relative_to(BASE).as_posix()}: {covered-expect!r}")
    if expect - covered:
        raise ValueError(f"Expected line(s) to be covered in {uut.relative_to(BASE).as_posix()} but they weren't: {expect-covered!r}")
    print("Line coverage good!")

if __name__=='__main__':
    main()
