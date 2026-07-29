# Auto Parts Market Analysis

## Goal

A data-driven tool that helps evaluate the potential of opening an auto parts store in a specific region using public data and geospatial analysis.

## Features

- ✅ Google Places competitor mapping (Google Maps)
- ✅ Workshop mapping (Google Maps)
- ⬜ Population analysis (IBGE)
- ⬜ Income analysis (IBGE)
- ⬜ Fleet analysis (SENATRAN)
- ⬜ Opportunity score

## Tech Stack

- Python
- Google Places API
- Pandas
- PostgreSQL *(planned)*
- Power BI
- Docker *(planned)*

## Architecture

```text
         pipeline.py
             │
     ┌───────┼───────┐
     │               │
     ▼               ▼
google_places   google_workshops
collector.py    collector.py
     │               │
     └───────┬───────┘
             ▼
         cleaner.py
             ▼
        analysis.py
             ▼
        exporter.py
             ▼
      Power BI / CSV
```

## Roadmap

- [ ] Create IBGE socioeconomic collector
- [ ] Create SENATRAN fleet collector
- [ ] Design PostgreSQL database schema
- [ ] Containerize the project with Docker
- [ ] Create Power BI dashboards

## Design Decisions

This project was designed to prioritize modularity, reproducibility and scalability from the beginning.

Some architectural decisions were intentionally made to simplify maintenance and future expansion.

### Why use independent collectors?

Each data source has its own collector.

This makes debugging easier, since failures can be isolated without affecting the rest of the pipeline.

### Why save raw CSV files before loading the database?

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