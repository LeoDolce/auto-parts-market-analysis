# Auto Parts Market Analysis

A data-driven geospatial analysis project designed to evaluate the commercial potential of opening an auto parts store in a specific geographic area.

The project combines business listings, demographic data, socioeconomic indicators and vehicle-fleet information to transform heterogeneous public and commercial data sources into a localized market opportunity analysis.

The final objective is not simply to identify where people live, but to identify locations where **potential demand, purchasing power, competition, workshops and accessibility** create a favorable environment for a new auto parts operation.

---

## Goal

The main goal of this project is to build a reproducible analytical pipeline capable of evaluating the potential of a local auto parts market.

The analysis is performed around a configurable geographic point and radius.

For the current study, a **2.5 km radius** was selected around the target location.

The project seeks to answer questions such as:

- How many people live inside the analyzed area?
- What is the socioeconomic profile of the population?
- How many auto parts stores already operate in the area?
- How many automotive workshops could represent potential B2B customers?
- What is the estimated local vehicle demand?
- Where are competitors concentrated?
- Which areas appear underserved?
- Which locations combine demand potential with lower competitive pressure and better accessibility?

The project is therefore structured in two analytical stages:

1. **Macro analysis** — evaluate the overall commercial characteristics of the selected market.
2. **Microgeographic analysis** — identify specific areas and locations with better commercial potential.

---

## Features

- Google Places competitor mapping
- Automotive workshop mapping
- IBGE Census 2022 demographic analysis
- Population allocation based on census-sector coverage
- IBGE socioeconomic analysis
- SENATRAN fleet data investigation
- Local fleet estimation through an explicit calibration assumption
- Geospatial processing using census-sector boundaries
- Competitor and workshop spatial analysis
- Dynamic market indicators
- Planned Power BI heatmap and opportunity scoring

---

## Data Sources

### Google Places

Used to identify:

- Existing auto parts stores
- Automotive workshops
- Geographic coordinates
- Place identifiers
- Other business information returned by the API

Google data represents the businesses returned by the API and should therefore not be interpreted as a guaranteed census of every business operating in the region.

---

### IBGE Census 2022

Used as the main demographic and socioeconomic source.

The project uses census-sector geographic boundaries together with demographic indicators obtained from IBGE data sources.

The geographic component is particularly important because the study area is defined by a radius rather than by administrative boundaries.

Instead of assigning an entire census sector to the analysis when only part of the sector falls inside the radius, the project calculates the proportion of the sector covered by the study area and allocates the corresponding population proportionally.

This produces a more representative estimate of the population actually located inside the analyzed perimeter.

---

### SENATRAN

SENATRAN fleet data was investigated as a potential source for estimating the number of vehicles operating within the study area.

During the analysis, significant limitations were identified.

The municipal fleet dataset for São Paulo contains a very large number of vehicles associated with the generic ZIP code `00000-000`, making direct geographic allocation by ZIP code unreliable.

The municipal total also appears to be affected by vehicles registered by organizations such as rental companies and corporations whose vehicles may operate outside the municipality.

For this reason, the raw municipal fleet is **not treated as a direct representation of the active local fleet**.

Instead, SENATRAN is used as an important diagnostic source for understanding the scale and limitations of the registered fleet.

---

## Architecture
                        pipeline.py
                             │
     ┌───────────────┬───────┴───────────────┬───────────────┐
     │               │                       │               │
     ▼               ▼                       ▼               ▼
google_places   google_workshops     ibge_demographics  senatran_fleet
collector.py     collector.py          collector.py      collector.py
     │               │                       │               │
     └───────────────┬───────────────────────┴───────────────┘
                     ▼
                 cleaner.py
                     ▼
                analysis.py
                     ▼
              Power BI / Excel

Each source is collected independently and preserved as raw data before further processing.

This architecture makes individual components easier to test, debug and replace.

## Why Independent Collectors?

Each external data source has its own collector.
This separation gives each module a clear responsibility.

For example:

If IBGE data cannot be collected, the IBGE collector can be investigated independently.
If SENATRAN data contains inconsistencies, the fleet collector can be inspected without modifying the Google Places logic.
If the Google API changes its response structure, only the corresponding collector should require modification.

This modular structure also makes it easier to add new data sources in the future.

## Why Preserve Raw Data?

Collected data is stored in the data/raw/ directory before being processed.
This creates an important separation between
data collection → data processing → analysis

Preserving the raw files provides several advantages:
- The analysis can be reproduced without making new API requests.
- Data transformations can be reviewed independently.
- API usage can be reduced.
- Errors in downstream processing can be investigated using the original dataset.
- Different processing strategies can be tested against the same source data.

The filenames also identify the data source and intended dataset, allowing the pipeline to determine which processing logic should be applied.

## Why Use a Geographic Radius?

The analysis is designed around the idea that an auto parts store primarily serves a geographically limited market.

A configurable radius allows the model to:

- Define a consistent study area.
- Avoid comparing arbitrary administrative boundaries.
- Reduce unnecessary API requests.
- Focus the analysis on the market surrounding a potential store location.

The current study uses a 2.5 km radius.

This value is a project assumption rather than a universal rule. Different business models or locations may justify a different radius.

## Spatial Population Allocation

A simple geographic filter would include every census sector touched by the study radius.
However, this can significantly overestimate population when only a small portion of a sector falls inside the analyzed area.
The project therefore calculates the intersection between each census sector and the study area.
The approximate population contribution of each sector is calculated as:

Allocated Population = Sector Population × Sector Coverage Ratio

This allows a sector that is only partially contained within the radius to contribute proportionally to the final population estimate.
GeoPandas and Shapely are used to perform the spatial operations.

## Fleet Estimation and Calibration

The raw SENATRAN fleet cannot be directly interpreted as the number of vehicles available to the local market.
For São Paulo, the municipal fleet is extremely large compared with the local population and includes vehicles that may not represent local household demand.
The dataset also contains a large volume of registrations associated with the generic ZIP code 00000-000.
This creates two important problems:
1. Geographic allocation of the registered fleet becomes unreliable.
2. Municipal fleet totals can overestimate the vehicle population actually relevant to the analyzed perimeter.

The project therefore uses an explicit calibration assumption:

Estimated Local Fleet = Population inside radius × Estimated Vehicles per Capita

The current model uses:
0.33 vehicles per inhabitant
This value is a modeling assumption, not an official IBGE or SENATRAN statistic.
The factor was introduced as a modeling assumption to avoid directly extrapolating the distorted municipal SENATRAN fleet to the study perimeter. The value should therefore be interpreted as an estimate used by the analytical model and can be changed as better local vehicle-ownership data becomes available.

This distinction is intentional:
Official data and model assumptions are kept conceptually separate.

## Income Calculation

Income is obtained at the census-sector level.
Because different sectors contribute different amounts of population to the study radius, the final regional income indicator should not simply be calculated as an unweighted arithmetic mean.
The project therefore uses the population allocated inside the radius as the weighting factor.
This prevents a small partially covered sector from having the same influence as a large sector containing hundreds of residents.

## Market Indicators

The current analysis produces indicators such as:
- Total population inside the perimeter
- Estimated average income
- Number of validated competitors
- Number of automotive workshops
- Estimated local vehicle fleet
- Vehicles per competitor
- Population per competitor
- Workshops per competitor

These indicators are intended to describe the market rather than independently determine whether a location should be selected.
The final location recommendation will be produced by combining multiple spatial factors.

## Limitations

The project intentionally documents limitations instead of treating imperfect datasets as ground truth.

1. IBGE

- Census data is aggregated at the census-sector level.
- The geographic allocation used by the project is therefore an approximation based on sector coverage and does not represent the exact location of every resident.

2. Google Places

- Google Places results depend on the businesses indexed and returned by the API.

Therefore:
- Some businesses may not be indexed.
- Some businesses may be incorrectly categorized.
- Search results should not be interpreted as a complete business census.

3. SENATRAN

The SENATRAN data presents significant limitations for local geographic analysis, in particular:

- A large portion of São Paulo's fleet is associated with 00000-000.
- Corporate and rental fleets can distort municipal totals.
- Vehicle registration location does not necessarily represent vehicle usage location.

For these reasons, the project does not treat the raw municipal fleet as the local market fleet.

## Calibration Assumption

The 0.33 vehicles per inhabitant factor is an analytical assumption.
It should not be presented as an official statistic.
The model was designed so that this parameter can be replaced when better local data becomes available.

## Future Development:

Microgeography Analysis:
The macro analysis provides a regional overview.
The next stage is to move from:
"Is this market attractive?"
to:
"Where exactly should a new auto parts store be located?"

The planned microgeographic analysis will combine:
1. Population Density: Identify areas with higher concentrations of potential consumers.
2. Purchasing Power: Use local income indicators to distinguish population density from effective purchasing potential.
3. Competitor Proximity: Calculate the distance between potential locations and existing auto parts stores.
4. Workshop Proximity: Identify areas with a concentration of automotive workshops that may represent B2B demand.
5. Main Roads and Accessibility: Give additional consideration to major roads and corridors with greater traffic, visibility and accessibility.
6. Spatial Heatmap: Combine the estimated demand, socioeconomic profile, competition and accessibility indicators into a visual opportunity map.
7. Opportunity Score: The final model will generate an opportunity score for candidate locations.

The exact weighting of each factor will be defined after the underlying datasets have been validated.

## Project Philosophy

This project was not designed around the assumption that public datasets are perfect. On the contrary, this project was developed recognizing that even official datasets are representations of real-world phenomena and may contain limitations, aggregation effects or geographic inconsistencies.

One of the main objectives is to identify where datasets fail to represent the real-world phenomenon being analyzed and to explicitly document the assumptions required to work around those limitations.

The analytical process therefore follows:

Collect
   ↓
Validate
   ↓
Identify limitations
   ↓
Transform
   ↓
Cross-reference
   ↓
Analyze
   ↓
Visualize

The final result is intended to be a decision-support tool, not a claim of absolute commercial certainty.