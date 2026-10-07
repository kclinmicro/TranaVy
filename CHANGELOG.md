# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [dev]

### Changed
- [#24](https://github.com/kclinmicro/emuse/pull/24) Changed rows in Summary statistics, adding corrected rows for Number of reads before and after qc and downsampling (by @AnnaNoren)

### Fixed
- [#25](https://github.com/kclinmicro/emuse/pull/25) Fixed bundled config path handling (reported by @ryanjameskennedy, fixed by @AnnaNoren)

## [1.1.0]

### Documentation

- Documented plans to support generating reports directly from raw Emu
  output, not just from a TRANA pipeline run (see the README "Roadmap"
  section) ([#15](https://github.com/kclinmicro/emuse/pull/15)).

### Changed

- Restructured the project into an installable `emuse` Python package to
  prepare for packaging as a bioconda recipe ([#15](https://github.com/kclinmicro/emuse/pull/15), [#17](https://github.com/kclinmicro/emuse/pull/17)):
  - Moved `make_report.py`, `templates/`, `static/`, `configs/`, and
    `taxonomy.tsv` into `emuse/` (bundled under `emuse/data/`).
  - Moved `make_report_test.py` to `tests/test_make_report.py`.
  - Added an `emuse` console script entry point.
  - Renamed the distribution/CLI name from `16s-report`/`make_report.py` to
    `emuse`.
- `pyproject.toml` now declares a proper `[build-system]`, package data, and
  MIT license metadata ([#17](https://github.com/kclinmicro/emuse/pull/17)).

### Added

- `LICENSE` (MIT) ([#17](https://github.com/kclinmicro/emuse/pull/17)).
- `MANIFEST.in` for sdist packaging ([#17](https://github.com/kclinmicro/emuse/pull/17)).
- Draft bioconda recipe at `recipe/meta.yaml` ([#17](https://github.com/kclinmicro/emuse/pull/17)).
- `THIRD_PARTY_LICENSES.txt` and a README "Acknowledgements" section crediting
  [Emu](https://github.com/treangenlab/emu) (MIT licensed), whose output this
  project parses and reports on ([#15](https://github.com/kclinmicro/emuse/pull/15), [#17](https://github.com/kclinmicro/emuse/pull/17)).

## [1.0.0]

Initial release of the report generator for the TRANA 16S rRNA taxonomic
profiling pipeline.

### Added

- HTML report generator that turns Emu/TRANA abundance and read-assignment
  output into a self-contained, styled report ([#1](https://github.com/kclinmicro/emuse/pull/1)).
- `--output_file` CLI parameter to control where the generated report is
  written ([#2](https://github.com/kclinmicro/emuse/pull/2)).
- Alignment-based metrics (percent identity and coverage) computed from
  Emu's alignment output ([#3](https://github.com/kclinmicro/emuse/pull/3)).
- Refined assignment metrics and a customizable negative control table in
  the report ([#4](https://github.com/kclinmicro/emuse/pull/4), [#5](https://github.com/kclinmicro/emuse/pull/5)).
- Normalised abundance calculation relative to a spike species, with the
  spike species later made configurable via `config.toml` instead of being
  hardcoded ([#8](https://github.com/kclinmicro/emuse/pull/8), [#9](https://github.com/kclinmicro/emuse/pull/9)).
- Test suite with fixtures based on realistic sequences ([#6](https://github.com/kclinmicro/emuse/pull/6)).

### Fixed

- Removed insertions (instead of deletions) from the `query_alignment_length`
  calculation, which had skewed coverage figures ([#10](https://github.com/kclinmicro/emuse/issues/10), [#11](https://github.com/kclinmicro/emuse/pull/11)).
- Report layout now adapts its dimensions to the browser window instead of
  using a fixed size ([#13](https://github.com/kclinmicro/emuse/issues/13), [#14](https://github.com/kclinmicro/emuse/pull/14)).

