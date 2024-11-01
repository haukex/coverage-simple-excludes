Changelog for ``coverage-simple-excludes``
==========================================

1.0.0 - 2024-11-01
------------------

- Fix a bug where `# cover-req-ltX.Y` was excluding a bit too much
- Made regular expressions slightly stricter:
  e.g. `# cover-not-linuxx` is no longer recognized as `# cover-not-linux`
- Internal optimizations
- Added support for `--debug=sys`
- Documentation updates

0.9.1 - 2024-10-09
------------------

- Fix `# pragma: no cover` not working

0.9.0 - 2024-10-09
------------------

- Initial release
