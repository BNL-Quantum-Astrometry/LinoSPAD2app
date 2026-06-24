# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-06-24

New "Full Sensor" tab, PyInstaller packaging improvements, MZI tab fixes.

### Added

- "Full Sensor" tab (`linospad2_dual_tab.py`, `plot_figure_dual.py`): plots
  both halves of the LinoSPAD2 sensor simultaneously (512 pixels on the
  x-axis). Includes two independent browse paths and motherboard selectors,
  shared daughterboard/firmware/timestamps controls, and split pixel-mask
  scroll areas (one per board). A dashed boundary line is always drawn at
  x = 255.5. Pixel-address correction is applied silently to board 2.

- `mplcyberpunk` added to `pyproject.toml` runtime dependencies.

### Changed

- `os.chdir()` calls replaced with absolute-path `glob` across all tabs
  (`live_timestamps_tab.py`, `MZI_tab.py`, `single_pix_hist_tab.py`) and
  `calibrate.py`. This makes the app work correctly when frozen by
  PyInstaller.

- `calibrate.py`: removed `pandas` dependency; calibration matrix is now
  saved with `numpy.savetxt`. `calibrate_load` updated to match the new
  headerless CSV format.

- `setuptools` removed from runtime dependencies in `pyproject.toml`
  (build-only tool, not needed at runtime).

- `main.spec`: added `mplcyberpunk` to `hiddenimports`, added `excludes`
  for unused packages (`pandas`, `tkinter`, `scipy`, `IPython`) to reduce
  bundle size, renamed output executable from `main` to `daplis-rtp`.

- MZI tab x-axis changed from file-count index to elapsed time in seconds
  (derived from file creation timestamps).

- MZI tab y-scale fixed: the upper limit no longer locks at a historical
  maximum. Both axes now autoscale each frame and share a common upper
  limit.

### Fixed

- All streaming tabs (`live_timestamps_tab.py`, `MZI_tab.py`,
  `linospad2_dual_tab.py`): catching `FileNotFoundError` and `OSError` in
  the inner data-read block so that removing data files while the stream is
  running shows an error dialog and stops the stream instead of crashing.

- `MZI_tab.py`: outer exception was catching `(IndexError, FileNotFoundError)`
  instead of `ValueError`, so an empty folder would crash rather than show
  the "no data files" dialog.

- `single_pix_hist_tab.py`: added `return` after the empty-folder error
  dialog to prevent a subsequent `UnboundLocalError` on `last_file`; wrapped
  the `plot_hist` call in its own `try/except` for the race-condition case
  where a file disappears between the directory scan and the read.

## [1.2.0] - 2025-06-17 #TODO

Flexibility and crash avoidance.

### Added

- Raw '.ui' files to the '.py' with the GUI tab information.

- Option for user input for the daughterboard and motherboard numbers.

### Changed

- Error check when no mask for the requested board combination is found. Does not crash now.

## [1.1.4] - 2025-05-04

Fixes (again).

### Changed

- Updated MANIFEST.in (again) so that it includes the '.txt' files to pypi.

## [1.1.3] - 2025-05-04

Fixes.

### Changed

- Updated MANIFEST.in so that it includes the '.txt' files to pypi.

## [1.1.2] - 2025-05-04

Mask call update.

### Changed

- How the '.txt' files with masks are called. No hard reversing on the path tree, works with every way of installation (manual, from github, pypi, distributable).

## [1.1.1] - 2025-01-28

Setup-file update.

### Changed

- Updated README with instruction on how to install and run the program.

- Added requirement for the 'qdarkstyle' package to the 'pyproject.toml' 
file.

## [1.1.0] - 2025-01-28

Adapted the package for installation via 'pip install'. Now, after
the package is installed, one can run it via 'daplis-rtp' command.

### Added

- Requirement for the 'qdarkstyle' package for dark-themed GUI.

### Changed

- The 'pyproject.toml' setup file: added a link to the 'main.py' so that
after installation the program can be run via 'daplis-rtp' from the 
terminal/command line.

### Removed

- The '.ui' files since they were changed to '.py'. Also, removed the
back-up copies of the second tab (single pixel histogram) UI.

## [1.0.1] - 2025-01-26

Minor fixes in all tabs, specifically regarding the canvas widget.

### Changed

- Fontsize in the plot widget in all three tabs.

## [1.0.0] - 2025-01-24

First official release to PyPI.

### Added

- This changelog.

### Changed

- Installation files: installation is now done using the 'pyproject.toml' 
file instead of 'setup.py'.

## [0.9.9] - 2025-01-24

Preparing the package for the official release

### Added

- Two boxes for the two top-most pixels (looked for automatically) in 
the live-timestamps tab for easier alignment.

### Fixed

### Changed

- The name of the package.

- The layout and size of the boxes in all tabs.

- The single-pixel-histogram tab to match its style to the other
two tabs.

### Removed

- Unused "mask_NL11_all.txt".
- Unused masks in "params/masks/old".
- Test leftovers in "tests/test_data/results".
