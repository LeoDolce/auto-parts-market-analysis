# Auto Parts Market Analysis

## Goal:

A data-driven tool that helps evaluate the potential of opening an auto parts store in a specific region using public data and geospatial analysis.

## Features:

✔ Google Places competitor mapping (Google Maps)
✔ Workshop mapping (Google Maps)
⬜ Fleet analysis (SENATRAN)
⬜ Population analysis (IBGE)
⬜ Income analysis (IBGE)
⬜ Opportunity score

## Tech Stack:

Python
Google Places API
Pandas
Power BI
SQL\
PostgreSQL (planned)
Docker (planned)

Architecture:

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

Roadmap:

Make population and income analysis -> IBGE_socioeconomic_data_collector.py
make fleet analysis -> SENATRAN_fleet_data_collector.py
Design PostgreSQL database schema
Create Power BI dashboards to show the analysis
Containerize the project with Docker