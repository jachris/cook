# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Libraries are automatically detected on Windows now as well
- C++ rules allow specifying `linkflags`
- Support for MSVC 2017
- Experimental rules for native Android apps
- New `timeout` parameter for `core.call()`
- Mechanism to prevent accidental deletes by using a wrong build directory

### Changed
- Using `cook --targets` will now list paths relative to the build directory
- Includes in system directories will now be tracked too
- Disabled restriction of output paths having to be in the build directory

### Fixed
- The task-failed handler was not properly protected against exceptions


## [0.2.0] - 2017-08-17
### Added
- Decorator to `core.cache()` function results 
- New generic rule `misc.run()`
- Basic option enumeration by using `cook --options`
- C++ toolchains are now public (`cpp.GNU` and `cpp.MSVC`)
- C++ compile time definitions are now properly translated by type
- Check if all options were consumed
- Loading scripts will now inject a `__file__` variable pointing to the script
- Automatic regeneration has been added to `examples/cpp/clion.py` 
- Warning when removing undeclared files in the build directory
- Add WIP (very basic for now) rules for external projects / build systems

### Changed
- Detect now all MSVC versions from 7.0 to 14.0 (2015)
- Globbing with `core.glob()` will return only files for now
- Exceptions and tracebacks are now correctly displayed
- `core.call` will now use all environment variables as a default

### Fixed
- `core.glob()` was not recursive under some circumstances
- Output paths were not properly verified
- `cpp.object` was using wrong paths if name was specified
- Messages regarding failed tasks could interleave
- Warning retrieval was broken


## 0.1.0 - 2017-07-27

Initial version.

[Unreleased]: https://github.com/jachris/cook/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/jachris/cook/compare/v0.1.0...v0.2.0
