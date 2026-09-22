# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Teco ("TEASER+eco") is an extension to TEASER+ / TEASER for computing environmental impacts (GWP/LCA) of
buildings, developed by e3D, RWTH Aachen University. It enriches CityGML/geometry data with material,
utility, and DIN EN 15804 environmental-indicator data, adds the **HUB4LCA building archetype typology**
(replacing TEASER's default TABULA archetypes), and drives Dymola/AixLib simulations via `buildingspy`.

The legacy GUI (`teaser/teaserplus_gui.py`, `gui_functions.py`) is dead — do not use, fix, or extend it.
Everything is used through the Python API/scripts under `teco/examples/`.

## Setup

Full walkthrough (Dymola/AixLib, submodule, env vars, troubleshooting) is in **INSTALLATION.md** — read it
before doing environment setup work. Key points:

- `teaser/` is a **git submodule** pointing at a private e3D fork of TEASER+, not the PyPI `teaser` package.
  Never `pip install teaser`; install it editable instead: `pip install -e ./teaser`.
- Then install Teco itself: `pip install -e .` followed by `pip install -r requirements.txt`.
- Teco and TEASER+ are developed in lockstep on matching branch names — when switching Teco to a feature
  branch (e.g. `hub4lca_archetypes`), check whether `teaser/` should be on the corresponding branch too.
- Running/simulating models requires Dymola + AixLib installed locally (not pip packages); this is not
  needed for pure Python-side code changes or most tests.

## Commands

```bash
pytest                                    # full test suite
pytest tests/test_tabula_sfh.py           # single test file
pytest --ignore=tests/test_modelicaversion.py   # skip the Dymola-dependent test
python teco/examples/e6_multi_building_gml_lca_manual_assign.py   # run an example end-to-end
flake8 --count --ignore W503,F401 --exclude teaser/data/bindings,doc,tests,.eggs --max-line-length=120
```

`test_modelicaversion.py` and anything that actually simulates requires a working Dymola/AixLib install;
expect it to fail in an environment without that.

## Architecture: how Teco attaches itself to TEASER+

This is the one thing that isn't obvious from any single file. Teco does **not** subclass TEASER+'s classes
in the normal Python way. Instead:

1. `teco/__init__.py` imports Teco's own `Building`, `ThermalZone`, `BuildingElement`, `DataClass`, etc.,
   then imports `teco.teco_module_modifications`.
2. `teco_module_modifications.py` rewrites `sys.modules`, so that `teaser.logic.buildingobjects.building`
   (and `.thermalzone`, `.buildingphysics.buildingelement`, `.data.dataclass`, `.logic.utilities`) now
   *point at Teco's modules*. Any TEASER(+) code that later does
   `import teaser.logic.buildingobjects.building` transparently gets Teco's version instead.
3. This is how TEASER archetype classes (`SingleFamilyHouse`, etc.) end up with Teco's LCA methods
   (`calc_lca_data`, `add_lca_data_heating`, ...) — they inherit from Teco's patched base classes once the
   archetype modules are (re-)imported after the patch runs.

Consequences for any code you write or edit here:

- **Import order matters.** Import something from `teco` (e.g. `teco.project.Project`) *before* importing
  any `teaser` archetype or CityGML module. If reversed, buildings won't get Teco's LCA methods.
- A side effect of the patch is that `sys.modules['teaser.logic.utilities']` ends up pointing at the `teco`
  *package* (not the `teco.logic.utilities` submodule), which breaks
  `from teaser.logic.utilities import get_default_path, ...` in code imported afterwards. The established
  workaround (see `teco/examples/e5_multi_building_gml_lca.py`) is to re-point
  `sys.modules['teaser.logic.utilities']` at `teco.logic.utilities` explicitly right after the `teco.project`
  import, before importing any further `teaser` submodules that need it.
- `teco/project.py`'s `Project` subclasses `teaser.project.Project` directly (normal inheritance, not the
  sys.modules trick) to add LCA-scenario parameters (`period_lca_scenario`, `use_b4`).

## Code layout

- `teco/logic/buildingobjects/` — patched replacements for TEASER's `Building`, `ThermalZone`,
  `BuildingElement` (adds LCA calculation methods).
- `teco/logic/buildingobjects/buildingphysics/` — EN15804 LCA data model (`en15804lcadata.py`) and material data.
- `teco/data/input/` — input data loading (materials, utilities, LCA data, building elements), including the
  archetype-assignment JSON data.
- `teco/data/output/` — CSV/report export for GWP and building-element results (`lca_csv_output.py`, etc.).
- `teco/examples/` — the actual usage surface. Each numbered `eN_*.py` script is a progressively more complete
  worked example (from plain EN15804 data lookup up to full multi-building CityGML LCA runs). Subfolders
  (`bausim2026/`, `phd2026/`, `energies2023/`, `bs2023/`) are self-contained use cases tied to specific
  publications, each with its own `README` naming the paper/thesis it belongs to — check that README before
  changing files in one of these folders, since inputs/outputs there are frequently tied to published results.
- `tests/` — mirrors TEASER's own test layout (`test_tabula_*`, `test_useconditions.py`, etc.) plus
  Teco-specific tests (`test_data.py`, `test_simulation_export.py`).

## Publication-tied example data

Several `teco/examples/*/` folders (and files like `bausim_2026_full.xlsx`) back specific published or
in-preparation papers/theses (see README.md's "Teco-related publications" list and each folder's own
`README`). Example CityGML/weather data in these folders has been deliberately anonymized for public release
— don't reintroduce identifying data when regenerating or editing these inputs.
