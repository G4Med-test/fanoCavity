# fanoCavity

**Fano cavity test**: dose deposited in an ionization chamber by a
mono-energetic 1.25 MeV gamma beam (Co-60-like), under charged-particle
equilibrium. Under idealized conditions the ratio of dose deposited to beam
energy fluence must equal the mass-energy-transfer coefficient of the wall
material — a stringent, closed-form check of EM transport self-consistency.

---

## 🔬 What this test does

The ionization chamber is modelled as a cylinder with a cavity (6 parameters:
wall material/radius/thickness, cavity material/radius/thickness; wall and
cavity share the same material with different densities to create the
equilibrium condition). A 1.25 MeV gamma beam irradiates the chamber and the
dose-to-fluence ratio is compared to the material's mass-energy-transfer
coefficient.

## 📚 Reference

- Source: `geant-validation-tests/src/fanoCavity`.
- E. Poon et al., *Phys. Med. Biol.* 50 (2005) 681.
- I. Kawrakow, *Med. Phys.* 27-3 (2000) 499.

## Import notes

- `main.cc`, `include/`, `src/` come from `fanoCavity.cc`/`include`/`src`.
- `macro/` contains the 3 macros found directly in the source tree
  (`basic.mac`, `run01.mac`, `vis.mac`, kept for reference but not listed in
  `validation/config.json`), plus 14 concrete, self-contained
  `standard_opt0_ROVER_<value>.mac` macros generated from
  `geant-config-generator/tests/geant4/fanoCavity/template.conf` +
  `params.conf` — these are the ones actually run by CI.
- `validation/parser.py` was **rewritten** for the `metadata()`/`parse()`
  module API that `ci-workflows/validation/export.py` actually calls (the
  first version, copied unmodified from
  `geant-config-generator/tests/geant4/fanoCavity/parser.py`, used the old
  `gts.BaseParser` class API and made CI fail with
  `AttributeError: module 'validation_parser' has no attribute 'metadata'`).
  See `validation/README.md` for what changed and why. The vendored `gts`
  package is no longer needed and was removed.
- A related variant, **`fanoCavity2`**, also exists in both source
  repositories (1.0 MeV mono-energetic **electron** source instead of
  1.25 MeV gamma, using a reciprocity-theorem approach per Sempau & Andreo
  2006). It was not imported as a separate repository since the slide lists
  only one "Fano cavity" item; `fanoCavity` (the gamma/Co-60 variant) was
  chosen as the canonical match.
