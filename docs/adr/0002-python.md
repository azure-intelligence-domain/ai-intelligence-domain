# 0002 — Python as the main language

- **Status:** accepted
- **Date:** 2026-10-16

## Context

We need one language for the mock systems, the platform flows and the
Intelligence domain (graph, retrieval, LLM orchestration, MCP server).

## Decision

Python 3.12+.

## Alternatives considered

- **TypeScript / Node.** Good MCP and API tooling, weaker data and AI
  ecosystem.
- **.NET / C#.** Closest to Azure-native services, but heavier for fast demo
  iteration.

## Consequences

- Strongest ecosystem for AI, MCP, graphs and data.
- Readable on a slide for a mixed business and technical audience.
- Requires a modern Python; the macOS system Python (3.9) is not used.
