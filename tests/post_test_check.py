#!/usr/bin/env python
import os
import re
import sys
from pathlib import Path
from importlib import import_module
from igbpyutils.error import init_handlers
import coverage

# This test checks to make sure that all lines in test_excludes.py
# are actually covered / excluded as defined by the comments.

EXPECT :set[str] = ({
    'import os',
    'import sys',
    'import unittest',
    'class ExcludesTestCase(unittest.TestCase):',
    'def test_excludes(self):',
    'stuff :set[str] = set()',
    'empty :list = []',
} | (
    {"if os.name == 'nt':", "stuff.add('is-nt')"}
    if os.name == 'nt' else {"stuff.add('not-nt')"}
) | (
    {"if os.name == 'posix':", "stuff.add('is-posix')"}
    if os.name == 'posix' else {"stuff.add('not-posix')"}
) | (
    {"if sys.platform == 'linux':", "stuff.add('is-linux')"}
    if sys.platform == 'linux' else {"stuff.add('not-linux')"}
) | (
    {"if sys.platform == 'win32':", "stuff.add('is-win32-1')"}
    if sys.platform == 'win32' else {"stuff.add('not-win32-1')"}
) | (
    {"if sys.platform != 'win32':", "stuff.add('not-win32-2')"}
    if sys.platform != 'win32' else {"stuff.add('is-win32-2')"}
) | (
    {"if sys.platform == 'darwin':", "stuff.add('is-darwin')"}
    if sys.platform == 'darwin' else {"stuff.add('not-darwin')"}
) | (
    {"if sys.implementation.name == 'cpython':", "stuff.add('is-cpython')"}
    if sys.implementation.name == 'cpython' else {"stuff.add('not-cpython')"}
) | (
    {"if sys.hexversion >= 0x03_0B_00_00:", "stuff.add('ge3.11')"}
    if sys.hexversion >= 0x03_0B_00_00 else {"stuff.add('lt3.11')"}
) | (
    {"if sys.hexversion < 0x03_0C_00_00:", "stuff.add('lt3.12')"}
    if sys.hexversion < 0x03_0C_00_00 else {"stuff.add('ge3.12')"}
) | (
    {"if sys.version_info.major >= 2:", "stuff.add('ge2.0')"}
    if sys.version_info.major >= 2 else {"stuff.add('lt2.0')"}
) | (
    {"if sys.version_info.major < 4:", "stuff.add('lt4.0')"}
    if sys.version_info.major < 4 else {"stuff.add('ge4.0')"}
) | { "self.assertEqual(len(stuff), 11)" }
)

_CMT_RE = re.compile(r'#.*?\Z')

BASE = Path(__file__).parent.parent

def main():
    init_handlers()
    sys.path.append(str(BASE))
    cov = coverage.Coverage(
        config_file=BASE/'pyproject.toml',
        data_file=BASE/'.coverage',
        #debug='sys',
    )
    cov.load()
    #cov.report(file=sys.stdout)

    mod = import_module('tests.test_excludes')
    # don't use cov.get_data().lines(filename) because that's all executed lines without exclusions
    fn, execs, excl, missing, missing_str = cov.analysis2(mod)
    uut = Path(fn)
    assert execs, execs  # executed lines (without excluded)
    assert excl, excl    # excluded lines
    assert not missing, missing
    assert not missing_str, missing_str

    with uut.open(encoding='UTF-8') as fh:
        lines = tuple(fh)
    covered = { _CMT_RE.sub('', lines[li-1].strip()).strip() for li in execs }
    errors :list[str] = []
    if covered - EXPECT:
        errors.append(f"Unexpected extra line(s) covered in {uut.relative_to(BASE).as_posix()}:")
        errors.extend( f"\t{ln}" for ln in sorted(covered-EXPECT) )
    if EXPECT - covered:
        errors.append(f"Expected line(s) to be covered in {uut.relative_to(BASE).as_posix()} but they weren't:")
        errors.extend( f"\t{ln}" for ln in sorted(EXPECT-covered) )
    if errors:
        for e in errors:
            print(e)
        print(f" Covered: {execs!r}")
        print(f"Excluded: {excl!r}")
    else:
        print("Line coverage good!")

if __name__=='__main__':
    main()
