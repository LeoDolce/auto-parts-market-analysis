# Auto Parts Market Analysis

## Goal

A data-driven tool that helps evaluate the potential of opening an auto parts store in a specific region using public data and geospatial analysis.

## Features

- ✅ Google Places competitor mapping (Google Maps)
- ✅ Workshop mapping (Google Maps)
- ⬜ Fleet analysis (SENATRAN)
- ⬜ Population analysis (IBGE)
- ⬜ Income analysis (IBGE)
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