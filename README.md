# Auto Parts Market Analysis

## Goal

A data-driven tool that helps evaluate the potential of opening an auto parts store in a specific region using public data and geospatial analysis.

## Features

- ✅ Google Places competitor mapping (Google Maps)
- ✅ Workshop mapping (Google Maps)
- ✅ Population analysis (IBGE Censo 2022)
- ✅ Income analysis (IBGE Censo 2022)
- ✅ Fleet analysis (SENATRAN 2026)
- ✅ Dynamic Opportunity Score Calculation

## Tech Stack

- Python (GeoPandas, Shapely, Pandas)
- Google Places API
- Power BI

## Architecture

```text
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
                exporter.py
                     ▼
              Power BI / Excel
```

## Roadmap

- [ ] Create interactive Power BI dashboards using the processed output data matrices

## Design Decisions

This project was designed to prioritize modularity, reproducibility and scalability from the beginning.

Some architectural decisions were intentionally made to simplify maintenance and future expansion.

### Why use independent collectors?

Each data source has its own collector.

This makes debugging easier, since failures can be isolated without affecting the rest of the pipeline.

### Why save raw data files before loading the database?

The raw files preserve the original collected data and allow the database to be rebuilt without making new API requests.

This reduces API costs and improves reproducibility.

### Why limit the search radius?

An auto parts store primarily serves nearby customers.

Using a configurable radius produces more realistic market analyses while also reducing unnecessary API requests and associated costs.

### Why combine different public datasets?

No single dataset is enough to evaluate business potential.

The project combines:
- Google Places → competitors and workshops
- IBGE → demographic and socioeconomic indicators
- SENATRAN → vehicle fleet characteristics

The value comes from integrating these sources rather than analyzing them separately.

## Limitations & Challenges

During development, specific nuances within Brazilian public datasets required strategic engineering decisions to guarantee data integrity.

### IBGE API Firewall & Cloudflare Challenges
- **Challenge:** The official IBGE Servidodados API implements aggressive anti-bot protection (Cloudflare Turnstile) and strict SSL verification, causing connection drops (`HTTP 403 Forbidden` and `SSLCertVerificationError`) during automated runtime environments.
- **Decision:** Shifted from live API streaming to a local-first approach. The pipeline now ingests the official 2022 Census Tract shapefiles (`.shp`) directly from `data/raw/IBGE/`, ensuring absolute execution resilience and sub-second performance.

### SENATRAN Regional Database "Blind Spots"
- **Challenge:** The national vehicle registry (RENAVAM) data structured by ZIP Codes (CEP) features extreme information decay. In the municipality of São Paulo, over 90% of the active fleet (~8 million vehicles) is registered under a generic fallback ZIP code (`00000-000`), making direct geographic filtering by neighborhood impossible.
- **Decision:** Implemented a Proportional Spatial Weighting allocation. The collector aggregates the absolute municipal vehicle volume and uses the precise demographic ratio calculated from the Censo 2022 block mesh to allocate vehicle density inside the target radius.

### Fleet Volatility Inflation (Rental Corporations)
- **Challenge:** The absolute vehicle numbers provided by SENATRAN for the capital of São Paulo generate an unrealistic 1:1 vehicle-to-person ratio (~0.88). This is heavily distorted by major corporate rental car companies that register millions of vehicles in São Paulo for tax purposes, although those vehicles operate nationwide.
- **Decision:** The calibration engine in `analysis.py` applies a socio-economically weighted brake. Using local household income indexes from the IBGE and regional mobility surveys, the active fleet is calibrated to a realistic ~0.33 vehicles per capita, mirroring the physical reality of the study perimeter.

### Google Places API Encoding Corruptions
- **Challenge:** Raw extractions from the Google Places API often cause encoding mismatch issues when processed by standard Windows table viewers, corrupting Portuguese diacritics into broken string patterns (e.g., "Auto Peças" becoming "Auto PeÃ§as").
- **Decision:** Enforced explicit UTF-8 parsing and automated string regex treatment during the early stages of the data cleaning and analytics workflow.

## Future Upgrades (Microgeography Analysis)

While the macro-analysis successfully validates the overall economic viability of the chosen 2.5km radius, commercial success depends on micro-location optimization (identifying exact streets with high demand but zero immediate competition). 

Planned upgrades to transition from regional metrics to localized routing optimization include:

### 1. Spatial Clustering & Heatmaps
- Implement Point Density Estimation (KDE) over the collected Google Places data coordinates to visually isolate competitor congestion hubs and pinpoint underserved geographical gaps ("commercial voids") within the perimeter.

### 2. Nearest Neighbors Analysis
- Leverage `shapely.ops.nearest_points` to dynamically calculate distance matrix thresholds between target B2B customers (workshops) and existing auto parts. This will automatically score and rank specific street sectors based on logistical isolation from competitors.

### 3. Voronoi Tesselation for Market Share
- Build Voronoi Polygons around competitor coordinates to define mathematical areas of dominance. By cross-referencing these localized cells with the population subsets from the IBGE census blocks, the model will estimate the micro-market share available for each specific city block.
