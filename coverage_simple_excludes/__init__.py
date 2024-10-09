"""
Simple ``coverage`` Exclusions
==============================

Please see the ``README.md`` that is part of this library for how to use this.

Author, Copyright, and License
------------------------------

Copyright (c) 2024 Hauke Dämpfling (haukex@zero-g.net)
at the Leibniz Institute of Freshwater Ecology and Inland Fisheries (IGB),
Berlin, Germany, https://www.igb-berlin.de/

This library is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This library is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see https://www.gnu.org/licenses/
"""
import os
import sys
from re_int_ineq import re_int_ineq
import coverage.plugin_support
import coverage.plugin
import coverage.types

# REMEMBER to update README.md when updating the following:
OS_NAMES :tuple[str,...] = ("posix", "nt", "java")
SYS_PLATFORMS :tuple[str,...] = ("aix", "emscripten", "linux", "wasi", "win32", "cygwin", "darwin")
SYS_IMPL_NAMES :tuple[str,...] = ("cpython", "ironpython", "jython", "pypy")

class MyPlugin(coverage.plugin.CoveragePlugin):
    def __init__(self) -> None:
        pass
    def configure(self, config: coverage.types.TConfigurable) -> None:
        # get config option
        exclude = config.get_option('report:exclude_lines')
        #print(f"Before: {exclude!r}", file=sys.stderr)  # Debug
        if exclude is None:
            exclude = []
        assert isinstance(exclude, list)
        # os / platform / implementation
        assert os.name in OS_NAMES, f"{os.name=} not in {OS_NAMES=}"
        assert sys.platform in SYS_PLATFORMS, f"{sys.platform=} not in {SYS_PLATFORMS=}"
        assert sys.implementation.name in SYS_IMPL_NAMES, f"{sys.implementation.name=} not in {SYS_IMPL_NAMES=}"
        nots :list[str] = [ os.name, sys.platform, sys.implementation.name ]
        only :list[str] = (
            [ x for x in OS_NAMES if x != os.name ] +
            [ x for x in SYS_PLATFORMS if x != sys.platform ] +
            [ x for x in SYS_IMPL_NAMES if x != sys.implementation.name ] )
        nots.sort()
        nots.sort(key=len, reverse=True)
        only.sort()
        only.sort(key=len, reverse=True)
        exclude.extend( f"#\\s*cover-{e}" for e in (
            'not-(?:'+'|'.join(nots)+')',
            'only-(?:'+'|'.join(only)+')',
            # + python version
            f"req-lt(?:{re_int_ineq('<=', sys.version_info.major, anchor=False)}\\.[0-9]+"
            f"|{sys.version_info.major}\\.{re_int_ineq('<=', sys.version_info.minor, anchor=False)})(?![0-9])",
            f"req-ge(?:{re_int_ineq('>', sys.version_info.major, anchor=False)}\\.[0-9]+"
            f"|{sys.version_info.major}\\.{re_int_ineq('>',  sys.version_info.minor, anchor=False)})(?![0-9])",
        ) )
        # write config option
        #print(f"After: {exclude!r}", file=sys.stderr)  # Debug
        config.set_option('report:exclude_lines', exclude)

def coverage_init(reg :coverage.plugin_support.Plugins, options :dict[str,str]):
    reg.add_configurer(MyPlugin(**options))
