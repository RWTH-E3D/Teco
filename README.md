![Teco - E3D RWTH Aachen University](./pictures/header.jpg)

# Teco - An extension to the TEASER+ tool for environmental impacts of buildings

<!---[![License](http://img.shields.io/:license-mit-blue.svg)](http://doge.mit-license.org)-->

Teco helps urban planners, policymakers, real estate asset managers, and simulation scientists determine whole-life carbon footprints and energy demands of buildings on a district scale, using basic building information.

The Teco extension is developed by members of the "Institute of Energy Efficiency and Sustainable Building (e3D), RWTH Aachen University" using Python 3.10+.
This extension is based on TEASER+ as well as the "Tool for Energy Analysis and Simulation for Efficient Retrofit (TEASER)" and can be used to import and export CityGML data sets with or without Energy ADE version 1.0. 

If you have any questions regarding Teco feel free to contact us at: [schildt@e3d.rwth-aachen.de](mailto:schildt@e3d.rwth-aachen.de).

If you have any questions regarding TEASER+ feel free to contact us at: [shamovich@e3d.rwth-aachen.de](mailto:shamovich@e3d.rwth-aachen.de).

## Description
 
Ambitious sustainability and carbon reduction goals in the building sector require the large-scale determination of environmental impacts. Building energy demands in the operational phase are a crucial element to be considered. To fully reflect the building life cycle, emissions from all life phases - construction, operation, dismantling, re-usage - have to be analysed. This goes in accordance with the 11th United Nations Sustainable Goal of making cities and human settlements sustainable. 
At the same time, this analysis is generally data-intensive. With the increasing availability of 3D building models, particularly CityGML datasets, using such data is advantageous to the UBEM community and the life cycle assessment workflow. Since CityGML data is mainly geometric, Teco offers an enrichment procedure for building materials, utilities and respective environmental indicators based on DIN EN 15804. Thus, the Teco extension enhances the existing feature set and abilities of the TEASER+ tool, and allows the integration of 3D city models for urban-scale, ecological life cycle assessments.

One of Teco's key novelties is the **HUB4LCA building archetype typology**, which replaces TEASER's default TABULA
archetypes. HUB4LCA provides more nuanced, region- and municipality-dependent archetypes for both **residential and
non-residential** building types (single/multi-family houses and apartment blocks alongside offices, retail,
education, health, culture, hospitality, and industrial buildings), further varied by adjacency (detached,
semi-detached, terraced). See [How to cite HUB4LCA](#how-to-cite-hub4lca) below for the underlying methodology and
data sources.

## Version

The current version of Teco is 0.9. Earlier releases (up to 0.6.0) introduced a graphical interface
(`gui/teaserplus_gui.py`) including a full simulation setup with buildings from CityGML, manually added buildings,
and an LCIA result display. **This GUI is no longer maintained or supported** — Teco is now used exclusively through
its Python API/scripts (see `teco/examples/`).
<br>
The TEASER+ used for this version is in turn based on TEASER 0.7.6. <br>
Teco uses OEKOBAUDAT EPDs according to EN 15804+A2.

## How to use Teco

Teco is an enrichment framework based on TEASER+ with a range of dependencies.
It is currently being developed using Python 3.10+.

### Installation & Dependencies

See **[INSTALLATION.md](./INSTALLATION.md)** for the full, step-by-step installation guide, including Dymola/AixLib
setup, the required Python dependencies, and why TEASER+ must be installed from the `teaser` git submodule rather
than from PyPI.

### How to contribute to the development of Teco

You are invited to contribute to the development of Teco. You may report any issues by sending us an email to [schildt@e3d.rwth-aachen.de](mailto:schildt@e3d.rwth-aachen.de).

## How to cite Teco
Heuristic Urban-Scale Life Cycle Assessment of Districts to Determine Their Carbon Footprints. Schildt, M., Cuypers, J. L., Malhotra, A., Shamovich, M., Frisch, J., van Treeck, C.. In Proc. 2022 Building Performance Analysis Conference and SimBuild co-organized by ASHRAE and IBPSA-USA (Vol. 10, pp. 309-317), September 2022, Chicago USA.
[Link to publication](https://doi.org/10.26868/25746308.2022.C035)

### Teco-related publications
+ Which platform, which answer? Benchmarking building energy and carbon KPIs across UBEM tools and LLMs. Schildt, M., van Treeck, C., Frisch, J. In Proc. BauSIM 2026, Zürich, Switzerland, 9.–11. September 2026 (DOI: TBD, paper not yet published).
+ District-scale energy and carbon footprint assessments of buildings. Schildt, M. PhD thesis, RWTH Aachen University, 2026. Thesis advisors: Frisch, J., Causone, F., van Treeck, C. A. [Link to publication](https://doi.org/10.18154/RWTH-2026-04474)
+ Sensitivity analysis of building archetypes for the life cycle assessment of districts. Schildt, M., Ponec, A., Tayeb, Y., Cupyers, J. L., Frisch, J., van Treeck, C. In Proc. 2023 Building Simulation 2023, 18th International IBPSA Conference and Exhibition, September 2023, Shanghai China. [Link to publication](https://doi.org/10.26868/25222708.2023.1154)
+ On the Potential of District-Scale Life Cycle Assessments of Buildings. Schildt, M., Cuypers, J. L., Shamovich, M., Herzogenrath, S. T., Malhotra, A., van Treeck, C., Frisch, J. In Energies 2023, 16(15), Special Issue Energy Efficiency through Building Simulation, June 2023. [Link to publication](https://doi.org/10.3390/en16155639)

## How to cite HUB4LCA
Archetype generation for the district-scale Life Cycle Assessment of buildings. Schildt, M., Cuypers, J. L., Heblikar, P., Shivaraju, S., van Treeck, C., Frisch, J. In Proc. Building Simulation 2025, 19th International IBPSA Conference and Exhibition, August 2025, Brisbane Australia.
[Link to publication](https://doi.org/10.26868/25222708.2025.1121)

## How to cite TEASER+
Urban energy simulations using open CityGML models: A comparative analysis. Malhotra, A., Shamovich, M., Frisch, J., & van Treeck, C.. Energy and Buildings, 255, 111658, January 2022.

## How to cite original TEASER

+ TEASER: an open tool for urban energy modelling of building stocks. Remmen P., Lauster M., Mans M., Fuchs M., Osterhage T., Müller D.. Journal of Building Performance Simulation, February 2017,
[pdf](http://dx.doi.org/10.1080/19401493.2017.1283539),  
[bibtex](https://github.com/RWTH-EBC/TEASER/tree/master/doc/cite_jbps.bib)

## License

Teco is released by RWTH Aachen University, e3D - Institute of Energy Efficiency and Sustainable Building, under the MIT License (see License.md).

## Acknowledgements

The developers of Teco would like to thank the Institute of Energy Efficient Building and Indoor Climate (EBC), E.ON Energy Research Center, RWTH Aachen University for their effort in developing TEASER and for making it available open-source. Furthermore, we would like to thank the German Federal Ministry of Housing, Urban Development and Construction for the ongoing development and open-source availability of OEKOBAUDAT.



