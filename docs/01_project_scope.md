# Project Scope

## Objective

The objective of this project is to build a data-driven decision support tool capable of evaluating the business potential of opening an auto parts store in a specific region.

Instead of relying solely on intuition, the project combines multiple public data sources to estimate market opportunities based on competition, potential demand and regional characteristics.

---

## Why this project?

Many business location decisions are based on personal perception or incomplete information.

This project aims to demonstrate how different public datasets can be integrated to support business decisions using data engineering, geospatial analysis and business intelligence techniques.

Although the initial use case is an auto parts store, the architecture was designed so that new data sources and analyses can be incorporated without major structural changes.

---

## Scope

The first version (MVP) focuses on four main dimensions.

### 1. Competition Analysis

**Source:** Google Places API

The project identifies existing competitors located inside a configurable search radius around the selected study area.

The objective is to understand the local competitive landscape.

Collected information includes:

- Business name
- Location
- Rating
- Number of reviews
- Business status

---

### 2. Related Businesses

**Source:** Google Places API

Vehicle repair workshops are mapped because they represent an important indicator of local automotive activity and may become potential business partners or customers.

---

### 3. Socioeconomic Profile

**Source:** IBGE

The project collects demographic indicators that help estimate the local market potential.

Initially, the analysis focuses on:

- Total population
- Population density
- Income indicators
- Age distribution

These indicators help estimate purchasing power and market size.

---

### 4. Vehicle Fleet Analysis

**Source:** SENATRAN

Vehicle fleet information is one of the most important variables for an auto parts business.

The project intends to analyze:

- Fleet size
- Vehicle age
- Fleet composition (cars, motorcycles, trucks, etc.)

Older fleets generally require more maintenance, while larger fleets indicate greater market demand.

---

## Why use multiple data sources?

No individual dataset is sufficient to determine whether a region represents a good business opportunity.

The project's value comes from combining independent sources into a single analytical model.

Instead of answering isolated questions, the goal is to answer a broader business question:

> Is this region attractive for opening an auto parts store?

---

## Architectural Decisions

The project follows a modular architecture.

Each module has a single responsibility.

Examples include:

- Google Places collector
- IBGE collector
- SENATRAN collector
- Database loader
- Analysis module
- Dashboard

This separation improves readability, simplifies debugging and allows each component to evolve independently.

---

## Search Radius

The analysis is performed inside a configurable radius around a central geographic coordinate.

This decision was made for two reasons.

First, auto parts stores primarily serve nearby customers, making local competition more relevant than city-wide competition.

Second, limiting the search area reduces unnecessary API requests, helping keep operational costs low while improving the relevance of the collected data.