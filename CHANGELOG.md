# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Decorator to `core.cache()` function results 
- New generic rule `misc.run()`
- Basic option enumeration by using `cook --options`
- C++ toolchains are now public (`cpp.GNU` and `cpp.MSVC`)
- C++ compile time definitions are now properly translated by type
- Check if all options were consumed

### Changed
- Detect now all MSVC versions from 7.0 to 14.0 (2015)
- Globbing with `core.glob()` will return only files for now
- Exceptions and tracebacks are now correctly displayed

### Fixed
- `core.glob()` was not recursive under some circumstances
- Output paths were not properly verified
- `cpp.object` was using wrong paths if name was specified
- Messages regarding failed tasks could interleave


## 0.1.0 - 2017-07-27

Initial version.

[Unreleased]: https://github.com/jachris/cook/compare/v0.1.0...HEAD
