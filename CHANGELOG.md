# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Removed

## [0.5.1] - 2019-04-12

### Changed

 - sly is now optional dependency (moving away from lex/yacc moa syntax)

## [0.5.0] - 2019-04-11

### Added

 - pypi release
 - initial documentation
 - benchmarks (addition, outer product, matrix multiply, compile time)
 - symbolic shapes only dimension is required at compile time
 - support for core operations 
   - (+-*/)
   - reduce(binop)
   - inner(binop, binop)
   - outer(binop)
   - indexing
   - arbitrary transpose
 - shape, dnf, onf compilation stages
 - onf stage is naive compiler (no loop reduction, loop ordering, etc.)
 - lex/yacc moa frontend and `LazyArray` frontend
