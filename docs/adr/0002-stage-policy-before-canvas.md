# ADR 0002: Validate context policy before the canvas

## Status

Accepted

## Decision

Run a two-condition context-policy experiment before building the canvas. Compare explicit user selection with automatic FTS5 retrieval across eight paired scenarios and three model runs per condition.

Proceed to a local canvas prototype only if explicit selection prevents at least two automatic-retrieval failures and introduces no additional primary failures.

## Consequences

- The first experiment uses the simplest usable interface.
- The canvas remains the product direction but does not confound the context-policy result.
- Results support a personal feasibility decision, not a market claim.
