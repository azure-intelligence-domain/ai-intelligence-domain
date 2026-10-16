# 0001 — Local-first demo, mapped to Azure

- **Status:** superseded by 0003
- **Date:** 2026-10-16

## Context

The goal is a demo and reference implementation of the talk, for client
sessions, trainings and future talks. It will not run in production or be
publicly available. The talk itself describes an Azure implementation (API
Management, Service Bus, Event Grid, Event Hubs, Fabric, Cosmos DB, AI Search,
Foundry).

## Decision

Run everything locally with Docker, using open-source equivalents. Each local
component maps one-to-one to the Azure service named in the talk (see the
README mapping table).

## Alternatives considered

- **Azure from day one.** Most faithful to the talk, but several services bill
  per hour even when idle (Fabric capacity, AI Search, API Management), and the
  deploy-and-check cycle is much slower while the basics are still being
  shaped.

## Consequences

- No cloud cost; the only external dependency is the LLM API.
- Fast iteration and easy reset of the demo scenario.
- Live demos work without cloud access (apart from the LLM).
- The Azure story is told through the mapping, not shown live. A later Azure
  deployment remains possible because components are kept swappable.
