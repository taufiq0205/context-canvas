# ADR 0001: Model work as a task context graph

## Status

Accepted

## Decision

- A workflow is a graph of durable task nodes.
- Agents, skills, sessions, and artifacts are task metadata or history.
- A directed edge only permits selected context to flow from one task to another.
- The first gate constructs inspectable handoff packages; it does not execute agents or enforce runtime isolation.

## Consequences

- The graph survives agent changes and session restarts.
- Execution order and blocking dependencies remain outside this graph.
- The first gate claims context inclusion control, not authorization.
