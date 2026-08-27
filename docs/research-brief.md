# Research Brief: User-Controlled Context Graphs for AI Chat

## Purpose

Determine whether a node-based AI chat interface creates meaningful user value beyond existing chat branching, workspace memory, retrieval systems, and visual workflow tools. This brief guides the research; it does not assume the concept is novel or recommend building a full product.

## Concept and background

The concept treats each conversation as a node and each directed connection as an explicit rule for what prior context may influence another conversation. A user might connect two independent research chats to a synthesis chat, choose whether each edge passes a summary or selected messages, inspect the transmitted context, and remove an edge before regenerating an answer.

Adjacent capabilities already exist. ChatGPT Projects supports branching while retaining the original thread and provides project-scoped context ([OpenAI, “Projects in ChatGPT”](https://help.openai.com/en/articles/10169521)). Open-source projects self-describe closely related behavior: DAG-chat represents messages as a directed acyclic graph with branch and merge operations ([DAG-chat repository](https://github.com/ZM-BAD/DAG-chat)); ThoughtDAG says incoming wires determine model context and lets users alter outputs by deleting edges ([ThoughtDAG repository](https://github.com/chenxiachan/thoughtdag)); Zermind combines chat with conversational mind maps and branching from nodes ([Zermind repository](https://github.com/okikeSolutions/zermind)). These are direct prior art to verify, not proof that the proposed interaction is differentiated.

## Problem statement

Long-running AI work is split across chats. Isolated chats lose useful context, while broad automatic memory can introduce irrelevant, stale, sensitive, or hard-to-explain information. The research must test whether explicit, inspectable context links improve outcomes enough to justify the effort and visual complexity they impose on users.

## Hypotheses

- **H1 — Control:** Users make fewer stale or irrelevant-context errors with explicit context links than with automatic cross-chat retrieval.
- **H2 — Provenance:** Users identify the source of an answer more accurately when inherited context and citations are visible.
- **H3 — Efficiency:** For multi-chat synthesis tasks, explicit links improve answer quality per input token versus passing all prior history.
- **H4 — Usability cost:** Creating and maintaining the graph adds tolerable effort only for recurring or complex work, not ordinary chat.
- **H5 — Differentiation:** A defensible gap exists only if explicit context permissions, inspection, and revocation are materially stronger than current branch/merge products.

## Research questions

1. Which jobs genuinely require context to move between independent conversations?
2. What does an edge mean: full transcript, selected messages, summary, live retrieval scope, or permission boundary?
3. Who should choose transmitted context—the user, the system, or both—and when?
4. Can users predict what a destination chat knows and explain why it knows it?
5. How should conflicts, edits, deletion, staleness, cycles, and source precedence behave?
6. At what graph size does navigation or maintenance become worse than search, folders, or project-scoped memory?
7. Which existing products already satisfy the target job, and what evidence remains for differentiation?
8. Does the approach improve correctness, provenance, privacy control, token use, or task completion time?

## Scope

Research:

- Directed links between independent chats.
- User-visible context selection, preview, citations, revocation, and staleness.
- Individual knowledge-work scenarios involving comparison, synthesis, and evolving decisions.
- Comparison with isolated chat, full-history/project context, automatic retrieval, and existing graph-chat tools.
- A small local prototype only if needed to test behavior.

Do not research or build yet:

- Biological-neuron simulation or claims of brain-like intelligence.
- Autonomous multi-agent orchestration.
- Automatic knowledge-graph extraction as the default architecture.
- Team collaboration, marketplace integrations, mobile clients, or production-scale infrastructure.
- A vector database unless a measured retrieval need exceeds simple transcript selection or full-text search.

## Prior-art map and starter primary sources

| Category | What to establish | Starter primary sources |
|---|---|---|
| Chat branching and scoped memory | Whether branches remain alternate timelines and what context boundaries users can control | [OpenAI Projects documentation](https://help.openai.com/en/articles/10169521) |
| Conversation/message graphs | Whether users can branch, merge, reconnect, replay, and inspect exact upstream context | [DAG-chat source and README](https://github.com/ZM-BAD/DAG-chat), [ThoughtDAG source and README](https://github.com/chenxiachan/thoughtdag), [tldraw Branching Chat source](https://github.com/tldraw/tldraw/blob/main/apps/docs/content/starter-kits/branching-chat.mdx), [Threadline source](https://github.com/terra901/Threadline), [Zermind source and README](https://github.com/okikeSolutions/zermind) |
| Long-term conversational memory | How systems manage context beyond a model window and across sessions | [MemGPT paper](https://arxiv.org/abs/2310.08560) and its linked code/data |
| Retrieval-augmented generation | Baseline retrieval, provenance, and updateability claims | [Lewis et al., RAG](https://arxiv.org/abs/2005.11401) |
| Graph-based retrieval | Whether graph construction helps the target multi-source questions enough to justify its cost | [Microsoft Research GraphRAG overview and publications](https://www.microsoft.com/en-us/research/project/graphrag/overview/) |
| Memory evaluation | Which tasks expose multi-session, temporal, update, and abstention failures; whether graphs beat simpler baselines | [LongMemEval](https://proceedings.iclr.cc/paper_files/paper/2025/file/d813d324dbf0598bbdc9c8e79740ed01-Paper-Conference.pdf), [Does Memory Need Graphs?](https://aclanthology.org/2026.acl-long.1232/) |
| Security and governance | Threats created when one chat can inject instructions or expose data to another | [OWASP LLM01 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/), [NIST AI RMF Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) |

For every candidate, inspect the product, documentation, source code, release history, and—where lawful and practical—the working interface. Record observed behavior separately from vendor claims. Search patents and academic literature before making any novelty claim.

## Methodology

### 1. Landscape review

- Define a reproducible search log: query, database/site, date, filters, and result disposition.
- Search product documentation, GitHub, arXiv/Semantic Scholar, ACM/IEEE libraries, and patent databases.
- Capture evidence in a feature matrix; cite the owning source for each claim.
- Test representative tools against the same scenario instead of comparing marketing copy.
- Treat “not found” as an open result, not proof of novelty.

### 2. User discovery

Recruit 8–12 people who regularly split one project across multiple AI chats (for example researchers, developers, analysts, or students). Use a 45-minute session:

1. Ask for a recent real example and reconstruct the current workflow.
2. Observe a synthesis task using their normal tool.
3. Give a paper prototype for connecting chats; avoid explaining the intended model first.
4. Ask participants to predict what the destination chat knows, find a source, remove stale context, and recover from an incorrect link.
5. Measure completion, errors, time, confidence, and maintenance burden; collect quotes only with consent.

Do not ask whether the idea “sounds useful.” Look for repeated behavior, costly workarounds, and willingness to use the controls unaided.

### 3. Technical feasibility experiment

Use the smallest implementation that can compare three conditions:

- **Isolated:** destination chat receives no cross-chat context.
- **Automatic:** a simple retrieval baseline selects context from all eligible chats.
- **Explicit graph:** only user-linked chats are eligible; the user can pass selected messages or a generated summary and preview the final prompt.

Start with local transcripts, SQLite, and full-text search. Freeze one model/version and inference settings where possible. Build 20–30 tasks containing conflicting facts, updated decisions, irrelevant chats, and one adversarial instruction embedded in a source chat. Use blinded human scoring plus deterministic checks where answers permit them.

Measure:

- Answer correctness and unsupported-claim rate.
- Source-attribution precision and recall.
- Stale/conflicting-information errors.
- Relevant-context precision and input tokens.
- Latency, task completion time, and user actions.
- Users’ accuracy when predicting included context.
- Leakage or instruction-following from unauthorized/untrusted chats.

Because the original RAG work identifies provenance and updating knowledge as open motivations for non-parametric memory ([Lewis et al.](https://arxiv.org/abs/2005.11401)), provenance must be evaluated as an outcome, not assumed from the presence of links.

## Comparison criteria

Score each approach with evidence, not a single weighted total:

| Dimension | Key test |
|---|---|
| Context control | Can the user include, exclude, preview, and revoke sources? |
| Mental model | Can the user correctly predict what the model receives? |
| Provenance | Can output claims be traced to exact messages or artifacts? |
| Conflict handling | Are newer, contradictory, and deleted sources handled visibly? |
| Retrieval quality | Does the system select relevant evidence without missing required context? |
| Usability | Does it reduce total effort on a real multi-chat task? |
| Scalability | Does it remain navigable and maintainable as chats and edges grow? |
| Portability | Can users export transcripts, links, and provenance in an open format? |
| Cost/performance | What are the token, latency, storage, and model costs? |
| Safety/privacy | Are boundaries enforced against leakage and indirect prompt injection? |

## Risks, ethics, and privacy

- Connected chats can propagate malicious instructions; OWASP notes that RAG and fine-tuning do not fully mitigate prompt injection ([OWASP LLM01](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)). Treat retrieved text as untrusted data and test authorization separately from relevance.
- Graph edges may reveal sensitive relationships even when message text is hidden. Minimize stored metadata and test export/deletion behavior.
- Summaries can erase qualifications or preserve deleted facts. Retain source pointers, mark generated summaries, and define refresh/invalidation behavior.
- User studies require informed consent, data minimization, redaction, controlled retention, and a withdrawal path.
- Do not market the biology metaphor as scientific equivalence. “Neuron” may also create naming and trademark confusion; assess naming separately.
- Use the NIST Generative AI Profile’s lifecycle approach to organize risk identification and evaluation rather than treating safety as a final checklist ([NIST AI 600-1](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)).

## Deliverables

1. Search log and annotated bibliography of primary sources.
2. Prior-art feature matrix with verified screenshots or source references.
3. Problem-interview synthesis with anonymized evidence.
4. Interaction model defining nodes, edge semantics, visibility, revocation, conflicts, and deletion.
5. Prototype and reproducible three-condition evaluation dataset/results.
6. Risk register and privacy/security requirements.
7. Final recommendation: stop, narrow, prototype further, or build an MVP.

## Decision criteria

Proceed to an MVP only if all are met:

- At least 5 of 8–12 participants independently demonstrate the same costly multi-chat problem.
- The explicit-graph condition materially improves at least one primary outcome—correctness, provenance, or unauthorized-context prevention—without materially worsening task time.
- Users can predict included context and revoke a source with at least 80% task success without coaching.
- The prior-art review identifies a specific unmet interaction or enforcement gap; a visual graph alone is insufficient.
- A simple transcript-and-edge architecture passes deletion, authorization, and prompt-injection tests.

Otherwise, narrow the concept to the strongest job or stop. Do not rescue weak evidence by adding graph databases, agents, or more interface features.

## Phased schedule (5 weeks)

| Phase | Time | Output / gate |
|---|---:|---|
| 1. Frame and landscape | Week 1 | Definitions, search protocol, source-backed prior-art matrix; gate: precise differentiation hypothesis |
| 2. User discovery | Week 2 | 8–12 interviews/usability sessions; gate: repeated high-cost job |
| 3. Interaction test | Week 3 | Paper/clickable prototype and revised edge semantics; gate: users understand context flow |
| 4. Technical evaluation | Week 4 | Minimal three-condition prototype and frozen benchmark results; gate: measurable benefit and enforced boundaries |
| 5. Synthesis | Week 5 | Findings, limitations, risk register, and go/narrow/stop recommendation |

Document assumptions, negative results, tool versions, model settings, and unverified product behavior throughout so the final conclusion is reproducible and does not overstate novelty.
