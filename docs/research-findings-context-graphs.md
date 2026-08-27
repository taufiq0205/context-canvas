# Research Findings: User-Controlled Context Graphs for AI Chat

**Phase 1 (Frame and landscape) + all evidence obtainable without human participants or a built prototype.**

Investigation date: 2026-08-27. Responds to [`docs/research-brief.md`](./research-brief.md).

---

## Executive summary

**The brief's core question — does a node-based AI chat interface create meaningful value beyond existing tools? — splits into two questions with opposite answers.**

**On the artifact: no meaningful gap. High confidence.** The proposed interaction model is not merely anticipated, it is *built, shipped, benchmarked, formalised in a paper, and partly patented*. [ThoughtDAG](https://github.com/chenxiachan/thoughtdag) (MIT, 289★, v0.3.31 released 2026-08-25) independently implements per-edge context semantics, a pre-send prompt preview, upstream-fingerprint staleness detection, prune-and-replay, and whole-graph isolation diagnostics — verified by reading its context-assembly source, not its README. Around it: ~20 further node-canvas branching-chat repos, most from 2026; **seven Obsidian Canvas AI plugins implementing ancestry-as-context since 2023**; a published formalisation ([CTA, arXiv 2603.21278](https://arxiv.org/abs/2603.21278), 2026-03); and **a granted US patent** (12,561,533 B1, filed 2025-08, granted 2026-02) claiming non-destructive branching with distinct contexts, user-selected message exclusion, and summary-injection-on-merge. "A visual graph of chats where edges control context" is a crowded commodity.

**On the evidence: a real and specific gap, and it is a human-evidence gap, not a feature gap. High confidence, from two independent negatives that converge.**

1. **The literature has never evaluated user-controlled context selection at all.** Across MemGPT, Lewis et al. RAG, GraphRAG, LongMemEval and Hu et al. (ACL 2026), greps for user-control vocabulary return zero hits. MemGPT does not merely omit it — it designs it out: memory management is *"entirely self-directed"* ([MemGPT §2.3](https://arxiv.org/abs/2310.08560)). Every benchmark's control points are system-side. **No published work supports or contradicts the brief's premise in either direction.**
2. **The closest prior art says the same thing about itself.** ThoughtDAG's own pre-registered design document states: *"Proving the UI beats linear chat for humans requires a separate HCI experiment (event-log instrumented; out of scope for v1)"* ([benchmark/DESIGN.md](https://github.com/chenxiachan/thoughtdag/blob/main/benchmark/DESIGN.md)).

So the most-developed implementation and the entire literature agree that the human question is open. That is the finding.

**Four narrow gaps survive scrutiny. None of them is the visual graph — which is the opposite of where the brief puts its emphasis.**

- **Enforcement-grade trust boundaries: absent everywhere, and unaddressed by the security standards too.** No tool examined enforces a permission boundary on an edge. ThoughtDAG's nearest approach is a *system-prompt instruction* telling the model to judge trust from bracketed labels ([`direct-llm.ts:60`](https://github.com/chenxiachan/thoughtdag/blob/main/src/lib/direct-llm.ts)) — precisely the class of mitigation OWASP LLM01 calls into question (*"it is unclear if there are fool-proof methods of prevention for prompt injection"*). The gap is corroborated independently: **NIST AI 600-1 contains zero occurrences of "trust boundar", "isolat", "segregat", "least privilege", "session" or "tenant" across 64 pages**, and OWASP's one use of "trust boundary" is a red-teaming note. Both standards assume the boundary runs *between principals*; nobody addresses one user's own two conversations. The brief's H5 requires "permissions, inspection, and revocation" to be materially stronger. **Inspection and revocation are shipped. Permissions are not — by any tool or any standard.**
- **Per-claim attribution across conversation links, and it has a standards mandate.** Gemini Notebook ships click-to-locate per-claim citations into *documents*; no tool does it for content arriving over a *user-drawn link between conversations*. NIST §2.8 defines high-integrity information as having *"a clear chain of custody"*, and NIST MP-3.4-001 asks directly whether end-users *"can accurately understand content lineage and origin."* Meanwhile OWASP LLM01's "segregate untrusted content" mitigation is *unimplementable at edge-traversal time* unless provenance was captured when the text was pasted. Cheapest gap to close, most likely to yield a measurable difference.
- **The full three-way per-edge transform — verbatim / selected messages / summary — is unclaimed across ~40 verified items.** ThoughtDAG implements two of three; CTA implements a binary and states in print that *"selective relevance filtering and compression are not yet implemented"*; Flowise has summarising memory but bound to a session key, never an edge; LibreChat has three selection modes but only as a one-shot copy at fork time. **This is the gap with an independent published paper naming it unsolved.**
- **Cross-*conversation* linking (as opposed to intra-canvas): unimplemented in the strongest tool.** ThoughtDAG's `partitionContext(nodeId, nodes, edges)` operates on one canvas's arrays; projects persist under separate IndexedDB keys (`thoughtdag:project:${id}`) and no node or edge carries a `projectId`. Genuine, but small — an unbuilt feature, not a defensible position.

**Recommendation: NARROW, then run one 3-day experiment. Do not build an MVP.** MVP is not an available conclusion — three of the brief's five decision criteria require participants and prototype runs that Phase 1 cannot adjudicate. The single highest-value next action is the one experiment nobody has run: **user-authored edges vs. automatic retrieval on the same corpus, with an adversarial injection arm.**

**One correction to the brief's H4 framing, from evidence that surfaced late.** Peer-reviewed user studies of node-graph LLM interfaces *do* exist — they study workflow graphs rather than conversation graphs, and they disagree. AI Chains (CHI 2022, N=20) found graph structure significantly improved transparency (*p*=.002) and controllability (*p*<.001) with no time penalty; VisCanvas (2026, N=20) found cognitive load *"indistinguishable"* from a chat baseline. ChainForge (CHI 2024) localises the cost to graph *mechanics* — *"needing to move nodes around… connecting nodes and deleting edges"* — not comprehension. **The graph may not reduce cognitive load, but it measurably improves the two properties the brief actually cares about.**

**What would change this assessment:** (a) the interview round finding that users *cannot* predict included context in an existing tool at ≥80% — that would kill the concept rather than support it, and is the cheapest disconfirming test available; (b) the automatic-retrieval arm matching explicit links on correctness *and* canary-emission rate, which would remove the last measured justification; (c) discovery of a shipped product enforcing edge-level authorization, which would close the only remaining defensible gap.

---

## Method and limitations

**What I did.** Verified every URL in the brief's prior-art table resolves and says what the brief claims. Shallow-cloned four of the named repositories and read their actual context-assembly functions rather than their READMEs. Fetched papers as PDFs and extracted text. Ran GitHub API searches for further prior art. Delegated five parallel primary-source strands with a contract requiring exact file paths, verbatim quotes, and raw URLs.

**Structural limitation — no observed behaviour for hosted products.** I have no account and no browser. For ChatGPT, Claude, Gemini, NotebookLM, Copilot and Perplexity, the "observed behaviour" half of the brief's rule 3 is *structurally empty*. Every claim about those products is a **vendor claim**, marked as such. This is a fact about evidence quality, not a hedge.

**Corollary — for the open-source tools, source code IS the observed behaviour,** and it is the strongest evidence in this report. It is also where the two most material findings came from, both of which contradict a README.

**One claim→observed upgrade I could not complete.** ThoughtDAG's benchmark numbers are a **first-party claim by the tool's author** (single run, temperature 0, synthetic English-only tasks, exact-match scoring, published 2026-08-21). The repository ships a zero-API re-scorer over immutable traces, so the claim is *reproducible in principle*; I did not execute it. Treat those numbers as first-party-unreproduced.

**On the brief's own citations: they held up better than expected.** All thirteen starter URLs resolved, including the two most rot-prone (the ACL 2026 Anthology link and the hash-based ICLR proceedings PDF). One brief claim is verified near-verbatim (RAG on provenance); one is materially misread (see below).

**Where the brief is wrong.**

- **"Does Memory Need Graphs?" does not say graphs lose.** The title is rhetorical. The paper's actual finding: *"the graph method consistently outperforms the flat index method across different model combinations. This gap becomes more pronounced as the dataset scale increases."* Its real headline is that unreported implementation details swamp the graph/no-graph axis. Citing it as evidence against graph memory would be a misreading. **But it is also not evidence *for* this concept** — it studies *automatically constructed* graph memory, not user-drawn edges. These must not be blurred.
- **The brief treats "inspect the transmitted context" and "remove an edge before regenerating" as design proposals.** Both are shipped features with source-code evidence, dated before this brief.
- **The brief under-weights that its §3 experiment largely exists.** ThoughtDAG's public benchmark (9 endpoints, 1,485 runs) is a superset of the brief's pollute/propagate/prune design — minus the one arm that matters most (automatic retrieval).

**Unverified cells in the matrix carry a reason** (JS-rendered / no public source / no account / not determined), never a bare mark.

---

## Prior-art feature matrix

Legend: **✅** implemented, verified in source or first-party doc · **⚠️** partial/qualified · **❌** absent, verified by exhaustive grep · **VC** vendor claim only, no observed behaviour · **?** unverified, reason given.

| Tool / system | Context control | Mental model | Provenance | Conflict handling | Retrieval quality | Scalability | Portability | Safety |
|---|---|---|---|---|---|---|---|---|
| **ThoughtDAG** ([src](https://github.com/chenxiachan/thoughtdag)) | ✅ Per-edge: solid=chain, dashed=reference with `contextDepth: 'quote'\|'full'` ([`graph.ts:110`](https://github.com/chenxiachan/thoughtdag/blob/main/src/lib/graph.ts)); archive=prune-but-keep; highlight-filter passes selected text only | ✅ Pre-send preview lists every message, role, 90-char head + token count, in assembly order ([`FollowUpInput.tsx:70`](https://github.com/chenxiachan/thoughtdag/blob/main/src/components/focus-panel/FollowUpInput.tsx)) | ⚠️ Node-level + PDF `p.N` page anchors; bracketed `[Reference:]`/`[Stale:]` labels. ❌ No per-claim→source-node attribution | ✅ `upstreamFingerprint` marks stale answers; `[Stale: …]` injected into downstream payload ([`context-builder.ts:94,115`](https://github.com/chenxiachan/thoughtdag/blob/main/src/store/context-builder.ts)); batch replay in dependency order | ✅ Benchmarked: subgraph-prune 162/162, recompute 161/162, source-only 152/162 (first-party, unreproduced) | ✅ Topology diagnostics: residual edges, shadow references, blind-pool breach, pool asymmetry ([`diagnostics.ts`](https://github.com/chenxiachan/thoughtdag/blob/main/src/lib/diagnostics.ts)); 3-tier zoom | ✅ JSON backup + Markdown export + folder autosave; imports ChatGPT/Claude exports | ⚠️ Untrusted text fenced + labelled; trust judgement delegated to the model by system prompt ([`direct-llm.ts:60`](https://github.com/chenxiachan/thoughtdag/blob/main/src/lib/direct-llm.ts)). ❌ No enforcement |
| **DAG-chat** ([src](https://github.com/ZM-BAD/DAG-chat)) | ⚠️ Multi-parent merge via citation chips → `parent_ids`; ❌ no per-edge transform | ⚠️ Chips show *which* nodes feed context; ❌ no prompt preview, ❌ no token count | ⚠️ `parent_ids` persisted (which nodes fed an answer); ❌ no per-claim attribution | ❌ None. Editing an ancestor silently changes descendants' context, no signal | ✅ Only repo with chain-preserving Kahn topological sort for merge ordering (`topological_sort_subdag`) | ⚠️ `max_depth=2000` BFS; no navigation aids | ❌ No export endpoint or client download | ❌ Nothing found |
| **tldraw Branching Chat** ([template](https://github.com/tldraw/branching-chat-template)) | ❌ Binding carries `{terminal, portId}` — geometry only, zero payload; all ancestors concatenated unconditionally | ❌ No preview, no token count | ❌ `MessageNode` is `{type, userMessage, assistantMessage}` — no source tracking | ❌ Zero `stale\|invalidat\|regenerate` hits repo-wide; downstream answers silently diverge | ⚠️ **Ordering defect on merges**: `getAllConnectedNodes` returns an unordered `Set`; `messages.reverse()` is correct only on a straight chain | ❌ Starter kit, no navigation aids | ⚠️ Inherits tldraw `.tldr` store only; no chat-shaped export | ❌ Worker forwards a client-supplied `ModelMessage[]` to Gemini with no validation and no system prompt |
| **Zermind** ([src](https://github.com/okikeSolutions/zermind)) | ❌ **Branching does not affect context.** `parentAgentMessageId` never reaches `streamText`; one Convex Agent thread per chat (`chats.ts:281`) | ❌ None | ❌ None | ❌ Structurally unnecessary — node structure has no bearing on context | ❌ Flat thread history regardless of node | ⚠️ `zermindNodes` holds `xPosition`/`yPosition`/`isCollapsed` — layout only | ❌ No export path found (share links ≠ export) | ❌ Nothing found |
| **Threadline** ([src](https://github.com/terra901/Threadline)) | ⚠️ Not a graph tool — a capture+RAG browser extension. User selects which retrieved memories to inject (per-*retrieval*, not per-edge) | ✅ **Only repo besides ThoughtDAG with a real pre-send preview**: results panel → user selects subset → injected as editable plain text. ❌ No token count | ✅ **Best of the OSS set**: `sessionId`, `originalMessageId`, `sourceUrl`, jump-to-source. ❌ Not per-claim | ❌ None for context (embedding sync is index freshness, not prompt invalidation) | ⚠️ Vector top-k across all captured sessions/providers | ⚠️ Per-session branch renderer, index-based grouping — not a cross-session graph | ✅ Versioned `threadline_v1_*.json` + 4 provider importers | ❌ Nothing found |
| **Gemini Notebook** (ex-NotebookLM) | **VC ✅ per-source include/exclude checkbox** — strongest shipped context control found | **VC ✅ published prompt-composition table** — Notes "only when you specifically select it"; Sources "the entire set or the subset you select" | **VC ✅ best in survey** — hover for full quoted text, click to navigate to the quote in context | ⚠️ not addressed | ✅ grounded only in your sources | ⚠️ not addressed | ❓ notebook export not addressed in retrieved docs | ⚠️ not addressed |
| **ChatGPT Projects + memory** | VC ⚠️ project-only vs default memory; branching is web-only, general (not project-scoped) | VC ✅ per-response sources panel + why-used — **but vendor states it "may not show every factor"** | VC ⚠️ source-level, not per-claim | ⚠️ not addressed | ⚠️ vendor-stated synthesis "may be broader than what can be shown" | ⚠️ not addressed | ✅ ≤7d; **excluded on Business/Enterprise** | ⚠️ not addressed |
| **Claude Projects + memory** | VC ⚠️ **no retroactive per-chat exclusion**; incognito is pre-emptive only | VC ✅ Topics list; search surfaces as a tool call | VC ✅ citations link back to original chats | VC ⚠️ topic-based, not conversation-summary | ✅ RAG past-chat search | ✅ separate memory space per project | ⚠️ **cannot import to another account** | ⚠️ not addressed |
| **Perplexity Projects** | VC ✅ **"Forking"** keeps prior thread's context in a fresh thread (Computer only, 06/18/26) | VC ⚠️ Brain tab shows generated memory | ⚠️ not addressed | ⚠️ auto/manual Brain control; no per-item revoke documented | ✅ per-project Brain | ✅ persistent hub | ❌ "transferring data between accounts is not supported" | ⚠️ not addressed |
| **CTA** ([arXiv 2603.21278](https://arxiv.org/abs/2603.21278)) | ⚠️ **binary only** — full parent context or clean window; *"selective relevance filtering and compression are not yet implemented"* | ❌ not mentioned | ❌ | ⚠️ names *logical context poisoning* as the failure mode | n/a — no evaluation | n/a | n/a | ❌ |
| **ChainForge** (CHI 2024) | ⚠️ "Past Conversation" edge input — **full history, no selection option** | ✅ **pre-run prompt preview** (one of only two found in ~40 tools) | ❌ | ❌ | n/a | ⚠️ cost localised to graph mechanics | ✅ open source | ❌ |
| **Obsidian Canvas AI plugins** (7 verified, since 2023) | ❌ **zero per-edge transforms** across all seven; control = connect/disconnect | ⚠️ one console debug dump (Augmented Canvas) | ❌ | ❌ | ⚠️ ancestor concatenation | ⚠️ | ✅ plain Canvas JSON | ❌ |
| **Flow editors** (Langflow, Flowise, Rivet, Dify, n8n, LangGraph, Prompt Flow) | ❌ **memory is session-keyed, never edge-carried** — *"Memory is node-specific and doesn't persist between different conversations"* (Dify) | ❌ post-run tracing only | ❌ | ⚠️ node-mediated trimming (Rivet), summarising memory bound to Session Id (Flowise) | ✅ mature | ✅ mature | ✅ | ⚠️ |
| **Mainstream branching clients** (LibreChat, Open WebUI, Msty, …) | ⚠️ LibreChat's 3 fork modes are genuine selection — **but a one-shot copy at fork time, not a link property** | ❌ | ❌ | ❌ | n/a | ✅ | ✅ | ❌ |
| **~20 further node-canvas chat repos** | ? Not individually source-verified — sampled by description only | ? | ? | ? | ? | ? | ? | ? |
| **MemGPT / Letta** ([paper](https://arxiv.org/abs/2310.08560)) | ❌ Designed out: *"entirely self-directed… without any user intervention"* (§2.3) | ❌ Not a user-facing concern | ❌ Not evaluated | ⚠️ Recursive summarization on eviction at ~70%/100% token watermarks | ✅ Evaluated on DMR + nested KV retrieval | ✅ Two-tier paging is the whole point | n/a | ❌ Not addressed |
| **RAG** ([Lewis et al.](https://arxiv.org/abs/2005.11401)) | ❌ System-side | ❌ | ⚠️ **Named in the abstract, never measured** — "provenance" appears exactly once in the paper | ✅ **Updateability IS measured**: index hot-swap, 70%/68% matched vs 12%/4% mismatched (§4.5) | ✅ Baseline | n/a | ✅ Raw-text memory is *"human-readable… and human-writable"* (§6) | ❌ Not addressed |
| **GraphRAG** ([paper](https://arxiv.org/abs/2404.16130)) | ❌ Graph auto-extracted by LLM from documents | ❌ | ❌ Measures comprehensiveness/diversity, not attribution correctness | ❌ Not addressed | ✅ Wins on *global sensemaking*, a different axis from cross-conversation recall | ⚠️ Indexing cost given only as wall-clock (281 min / ~1M tokens); no token figure published | ✅ Active, MIT, v3.1.2 (2026-08-21) | ❌ Not addressed |
| **LongMemEval** ([ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/d813d324dbf0598bbdc9c8e79740ed01-Paper-Conference.pdf)) | ❌ Control points are system-side: value, key, query, reading strategy | ❌ | ❌ | ✅ Tests knowledge updates + abstention explicitly | ✅ 30–60% drop vs oracle retrieval on ~115k-token histories | ✅ S (~50 sessions) and M (500 sessions) settings | ✅ Public benchmark | ❌ Not addressed |
| **Hu et al., "Does Memory Need Graphs?"** ([ACL 2026](https://aclanthology.org/2026.acl-long.1232/)) | ❌ Automatic construction only | ❌ | ⚠️ Notes graph indexes "contribute to interpretability" then documents failures — treated as intuition, not a scored outcome | ⚠️ Evaluated on LongMemEval + HaluMem | ✅ **Graph beats flat on retrieval, gap widens S→M**; loses when Value=Key or extractor is weak | ⚠️ Graph retrieval 574ms vs flat 240ms at M; extraction 2.1s vs 0.5s/session | ✅ [Code](https://github.com/AvatarMemory/UnifiedMem) | ❌ Not addressed |

---

## Per-source findings

### ThoughtDAG — the closest prior art by a wide margin

**What it is.** An MIT-licensed infinite-canvas desktop/web app (`chenxiachan/thoughtdag`, created 2026-02-17, 289★, 27 forks, last push 2026-08-25). Release cadence is extraordinary: **v0.3.31 on 2026-08-25**, with 31 tagged releases since 2026-08-13 — often several per day. Its stated rule: *"Wires are the context. What the model sees is exactly what wires into the node. Editing the graph edits the model's memory."*

**What it actually does — from `src/store/context-builder.ts` and `src/lib/graph.ts`, not the README.**

Context is a three-layer partition, not a flat ancestor walk. From `partitionContext`:

> *"Layers by HOW content enters (the One Rule, ordered): materials — content nodes… references — dashed edges: fenced [Reference] blocks (quote or full)… mainline — solid edges: the live conversation, strict chain order. A reference never forwards its own references (one level of indirection)."*

**The edge is genuinely a transform boundary, not a routing line** — the single most important finding for H5. `partitionContext` splits `edges` on `e.data?.isCrossLink`; cross-links become `ContextReference` records carrying `depth: edge.data?.contextDepth === 'full' ? 'full' : 'quote'`. A quote-depth edge emits the source's Q/A plus a one-line ancestor trail; a full-depth edge emits the whole upstream transcript. The user toggles this per edge (`setCrossLinkDepth`), and converting dashed→solid runs a cycle guard that refuses the change.

Note the deliberate design choice the code documents, which the brief's framing does not anticipate:

> *"Amounts are controlled on NODES (collapse+summary, highlight filter, archive) — edges only decide identity."*

So ThoughtDAG splits the brief's conflated "edge semantics" into edge=identity and node=volume. That is a considered answer to the brief's research question 2, arrived at independently.

**Determinism is an explicit design property**: *"This ordering is deliberately independent of edge creation history: the same graph always produces the same prompt."*

**Staleness is real and unusually careful.** `upstreamFingerprint` hashes everything a node depended on with the node's own content blanked out, normalizing away collapse state and generated summaries so *"a background summary arriving (or a card being folded) never fakes an 'upstream changed' signal downstream."* Drift marks the node stale, and stale answers enter downstream context prefixed `[Stale: this answer was written against an earlier version of its upstream]`. Nodes generated before fingerprinting are never flagged — *"honest: unknown provenance, not known-stale."*

**Isolation is checked statically.** `runDiagnostics` includes a **blind-pool breach** test — for sibling branches meant to be independent, it detects whether one can reach another, and a **pool asymmetry** test the source describes as detecting *"someone fed one juror extra evidence."* This is the brief's authorization dimension, implemented as graph-theoretic static analysis with one-click fixes.

**The preview requirement is met.** `FollowUpInput.tsx:70` calls `buildContext` and renders every message with role, a 90-character head, and a token count, in assembly order, plus a `backgroundHeavy` amber flag when materials+references exceed the live conversation. The code comment states the intent: *"What would a follow-up from this node actually send? Makes the core 'you control the context' promise visible before asking."*

**It has already run the brief's §3 experiment.** `benchmark/` contains a pre-registered design (drafted 2026-08-16), 9 model endpoints across 4 vendors, 1,485 runs, published 2026-08-21. Its core question: *"After wrong, outdated or irrelevant information propagates through a multi-turn conversation, how much answer quality do explicit context pruning and recomputation recover, and how does that recovery decay with propagation depth?"*

Headline results (**first-party, unreproduced**): harm split identical across all nine endpoints (misinformation 9/9, temporal-supersession 9/9, irrelevant-distractor 0/9); repair hierarchy subgraph-prune 162/162 > recompute 161/162 > source-only 152/162. **Deleting the message that introduced an error is often insufficient because contaminated downstream replies still carry it.**

The methodology is more rigorous than most product benchmarks: conditions are graph transformations rather than hand-picked message lists; an independent reference compiler cross-checks the product's own `buildContext` for node-sequence equivalence (explicitly to fix circularity — *"defining interventions in ThoughtDAG to prove ThoughtDAG's interventions work"*); the statistical unit is the family with depth variants treated as paired repeated measures; and `STATUS.md` records **withdrawn claims after user audits**, including a reasoning-ablation framing retracted on 2026-08-21 and a Fisher-exact test corrected to McNemar on 2026-08-23.

**What it does NOT do.**
- ❌ **No cross-canvas edges.** `partitionContext(nodeId, nodes, edges)` operates on the active canvas. Projects persist under `thoughtdag:project:${id}` with no `projectId` on nodes or edges. Two *separately stored* conversations cannot be wired together — only nodes within one canvas.
- ❌ **No per-claim attribution.** Web citations are `[n]` URL citations from the provider; PDF provenance is `p.N` page anchors. Nothing maps a sentence in an answer back to the upstream node that supplied it.
- ❌ **No enforcement.** The only trust mechanism is a system-prompt directive: *"Bracketed markers such as [Note], [Reference: …], [Link snapshot: …] … are provenance labels attached to your context by the canvas. Use them to judge where information came from and how much to trust it."* This delegates the trust boundary to the model.
- ❌ **No human study.** Stated by the authors, not inferred.
- ⚠️ Full-text preview is truncated to 90 characters per message.

### DAG-chat

Python/FastAPI backend + React frontend, 69★, created 2025-08-13. The **only repo of the four with a real release cadence** (v1.3.2), though recent commits are dependency bots only.

`build_history_from_parent_ids` runs a bounded upward BFS from `parent_ids` (`max_depth=2000`), then a chain-preserving Kahn topological sort, then flattens to `{"role", "content"}`. It is **the only implementation in the set that solves merge ordering correctly.**

The edge is `parent_ids: list[str]` on a message node — a pure routing line. Every reachable ancestor is concatenated verbatim; there is no per-edge choice of any kind. Multi-parent merge is genuinely user-driven via citation chips (`parentIds = citations.map(c => c.id)`). One root per conversation, so merging is intra-conversation — though notably the backend query filters on `_id` only, **never on `conversation_id`**, so cross-conversation merge would be accepted by the API while being unreachable from the UI.

**Does NOT do:** no prompt preview, no token counting, no staleness (editing an ancestor silently changes every descendant's future context with no signal), no export path at all, no per-claim provenance, nothing on safety. README claims match the code — the most honest of the four.

### tldraw Branching Chat

The brief's URL resolves (200). The template source lives at `tldraw/branching-chat-template` (16★, created 2025-09-17); **every recent commit is a mechanical SDK version bump.** A maintained-but-frozen demo, which fits its role as a starter kit.

`handleSend` in `MessageNode.tsx` calls `getAllConnectedNodes(editor, shape, 'end')`, pushes each ancestor's assistant and user messages, and calls `messages.reverse()`. The worker is a stateless pass-through that deserializes a client-supplied `ModelMessage[]` and forwards it to Gemini with **no validation and no system prompt**.

**Ordering defect on merge topologies.** `getAllConnectedNodes` is an unordered BFS returning a `Set`. On a straight chain, BFS order is child→parent→grandparent and `reverse()` restores conversation order. On a diamond or any merge, the BFS interleaves upstream branches by frontier depth, and `reverse()` produces an order that is neither chronological nor topological. There is no `parentId`, timestamp, or sequence number to sort by. The docs' claim — *"AI responses consider the entire conversation branch history"* — is accurate on *what* and silent on *order*.

This is the sharpest contrast in the set: **DAG-chat and tldraw solve the same graph problem, and DAG-chat wrote an 88-line topological sort for exactly the case tldraw handles with `Array.prototype.reverse()`.**

**README mismatch:** the Architecture section claims *"Durable Objects: Stateful operations and session management."* The worker contains zero Durable Objects — it is a stateless `WorkerEntrypoint` with an `itty-router`. Boilerplate copied from another template.

### Zermind — the brief's citation does not survive source inspection

The brief cites Zermind as combining *"chat with conversational mind maps and branching from nodes."* **The code does not support the context half of that claim.**

`parentAgentMessageId` is accepted by the `send` action, passed straight through to `zermindNodes.ensureForAgentMessages` for node bookkeeping, and **never reaches the model**. Verified three ways: (1) the `streamText` call passes only `{userId, threadId}` and `{prompt, model, temperature}` — no parent, no `contextOptions`, no message filter; (2) `zermindAgent.createThread` appears exactly once repo-wide (`chats.ts:281`), at chat-creation time, so **every branch in a chat shares one thread ID**; (3) the `zermindNodes` table stores `xPosition`, `yPosition`, `isCollapsed`, `isLocked`, `branchName` — layout and presentation fields only.

**Consequence: branching from node A vs node B in the same chat sends the model identical context.** The mind map is a visualization layer over a linear transcript. The README's *"Resume from any node and create alternate paths"* is true visually and false in the prompt-context sense.

7★, zero releases, currently mid-migration from Next.js to TanStack Start. Its genuinely built-out parts are collaboration, presence, and BYOK key management.

### Threadline — miscategorised by the brief

Not a branching-chat DAG app. A Plasmo/MV3 browser extension that captures conversations from five providers into IndexedDB, embeds them locally, and injects retrieved memory into the *host site's* composer. `formatRAGPrompt` is a 22-line file that wraps top-k results in `--- Memory N ---` blocks.

Notable despite the miscategorisation: it has **the best provenance and the best portability in the OSS set**, and it is one of only two tools with a real pre-send preview — the user sees matched source text, selects a subset, and the result is injected as *editable plain text* they can inspect before sending. Its "memory graph" is a per-session, index-based branch renderer (`roundIndex`/`branchIndex`), not a cross-session graph. Cross-conversation merging happens by default, but via embedding similarity, never via a user-authored link.

### The long tail — ~20 further implementations

A GitHub API search for branching-canvas chat descriptions returned a dense field, nearly all created in 2026. A representative sample:

| Repo | ★ | Last push | Self-description (verbatim, truncated) |
|---|---|---|---|
| `acrognale/llmtree` | 22 | 2024-08-25 | "places chats on an infinite canvas, allowing users to fork and branch conversations" |
| `PaoloJN/ai-chat-tree` | 11 | 2024-07-31 | "Obsidian plugin for hierarchical AI-driven conversations… within canvas notes, preserving context" |
| `Elliott-Crosby/Nodea` | 6 | 2026-08-19 | "Branching AI chat canvas: fork any reply, compare branches, never lose context" |
| `zendegani/canvas-chatbot` | 4 | 2026-08-15 | "break free from linear chat threads… branch conversations, and orchestrate multiple AI models" |
| `KarimTalbi/Leinwand` | 1 | 2026-06-08 | **"each node only sees the context of its connected ancestors — giving you branching, merging, and fine-grained control over what each interaction knows about"** |
| `STR7ANGER/Chat-Domain` | 1 | 2026-03-29 | "Each node inherits context from its parents" |
| `VRER1997/fugue-chat-tree` | 1 | 2026-02-02 | "thread branching, context slicing, and markdown export" |
| `MrToyy/convosketchpad` | 1 | 2026-08-13 | "explore ideas in parallel, compare and merge results" |
| `yule1048596-art/nonlinear-chat` | 1 | 2026-07-30 | "Turn AI chat from a timeline into a DAG — branch, compare, and merge contexts" |
| `johannesrgrr/BranchrOSS` | 0 | 2026-06-03 | "Open-source structured AI chat canvas with clean branch context" |
| `ConfidentProgrammer/branching-llm-engine` | 0 | 2026-08-12 | "pointer-based tree database, ancestry-filtered vector RAG" |

**These are description-level evidence only — none was source-verified.** Given that two of the four repos I *did* verify had README claims their code does not support, assume this list overstates capability. The point is not that any one is strong; it is that **the concept space is saturated**, and a claim of novelty for "visual graph of chats where edges carry context" is not sustainable.

### Obsidian Canvas AI plugins — ancestry-as-context has shipped since 2023

This kills any residual novelty claim on the core mechanic. A verified sweep found seven Obsidian Canvas AI plugins, the earliest from 2023, all implementing "walk incoming edges, concatenate ancestors, send":

- **`rpggio/obsidian-chat-stream`** (144★, 2024-07-31): *"Ancestor notes/files are included in the chat context. You can quickly create chat streams, and control what other notes are sent to the AI."* Control is connect/disconnect — topology only.
- **`MetaCorp/obsidian-augmented-canvas`** (123★, 2024-11-24): *"The links between notes are used to create the chat history sent to GPT."* Notably, an edge can carry a **question** — *"the question is placed on the link between the two notes"* — a prompt on the edge, but still not a context transform. It is also one of only two tools found anywhere with any prompt preview: a debug console dump.
- **`jcollingj/caret`** (200★): `getLongestLineage(nodes, edges, node_id)` walks edges structurally with **no edge-label reads**. README: *"no longer being actively maintained."* Its docs site `caretplugin.ai` is dead (DNS).
- **`AndreBaltazar8/obsidian-canvas-conversation`** (104★, 2023-03-18): has **no edges at all** — its own TODO says *"Add edges between nodes (no easy way of doing it right now)."*

**Zero per-edge transforms across all seven.**

### The closest published formalisation — and it names this report's gap as an open problem

**Conversation Tree Architecture (CTA)**, [arXiv 2603.21278](https://arxiv.org/abs/2603.21278) (2026-03-22, cs.CL). Formalises conversations as a directed rooted tree where each node has an isolated local context window and *"information passes between nodes only through defined flow operations"* — downstream, upstream merge, and general cross-node transfer where *"ρ specifies direction, selection criteria, and merge policy."* It names the failure mode **logical context poisoning**. Prototype in React + React Flow.

**Its implemented edge transform is binary, and the paper says so explicitly:** *"on branch creation, the user selects whether to pass the full parent context or start the child with a clean window"*, and *"Downstream passing supports full-context or no-context transfer; **selective relevance filtering and compression are not yet implemented**."* The paper poses *"should units be passed verbatim, as extractive summaries, or as abstractive compressions?"* as an **open design problem**.

**This is the single most useful citation in the report for positioning.** An independent 2026 formalisation of exactly this concept identifies the brief's per-edge transform question as unsolved — which both corroborates that the gap is real and demonstrates that others are converging on it. It is a design-space paper with **no user study**. Note it is filed under cs.CL, so a cs.HC-only search misses it.

### Flow editors — the edge is a typed wire; memory is session-keyed, never edge-carried

Verified across ten tools (Langflow 153,708★; **Flowise 55,395★ — now ARCHIVED**; Rivet 4,680★; Dify 153,579★; n8n 202,503★; LangGraph; Azure Prompt Flow; Google Visual Blocks; `heshengtao/comfyui_LLM_party`), a uniform finding: **no edge carries a user-chosen context transform.** Control over what reaches a downstream node is exercised by *inserting a node on the wire* or a *per-node toggle*, and **memory is keyed by session/thread ID, not by graph topology** — two nodes share history because they share a session key, not because an edge connects them.

Dify states it most plainly: *"Memory is node-specific and doesn't persist between different conversations."* Flowise is the strongest summarising-memory hit — *Conversation Summary Memory* *"creates a brief summary of the conversation over time"* — but it is a per-agent-node component bound by `Session Id`, not an A→B edge property. Rivet's `Trim Chat Messages` trims *"until the total length… is under the configured token length"* — node-mediated and positional, not semantic.

**ChainForge is the closest named-edge precedent:** *"Chat Turns work by connecting the output of an initial Prompt Node to the **'Past Conversation'** input of the Chat Turn node"* — an edge whose semantic is literally "the prior conversation." But it carries the **full history with no selection or summarisation option**.

### Prompt preview is nearly absent across the entire field

Across ~40 verified tools, a genuine **pre-run** assembled-prompt preview exists in exactly two places: **ChainForge** (hover the Prompt Node list icon to see all generated prompt combinations before Run) and **ThoughtDAG** (per-message list with token counts). Augmented Canvas has a developer-console dump. Rivet's dedicated Prompt Designer documentation is literally `TODO`. Everything else — Langflow message logs, Dify Variable Inspector, n8n INPUT/OUTPUT, Prompt Flow traces, LangGraph thread log — is **post-run tracing**, which is a different thing entirely.

### Mainstream branching clients — fork is a one-shot copy, not a link

TypingMind, LibreChat, Open WebUI, Msty, Cherry Studio, AnythingLLM and Perplexity are linear-transcript clients with branch navigation derived automatically from edit/regenerate/fork. The strongest counterexample still falls short: **LibreChat's fork** offers three modes — *"Copies only the visible messages: the direct path… excluding any branches"*, the path plus branches along it, or *"every message leading up to the target, including neighboring branches."* That is genuine user-chosen context selection — but as a **one-shot copy strategy at fork time**, not a reusable, inspectable, revocable link property, with no summarise option and no canvas. **Open WebUI:** *"The Fork chat action… copies the history from the start of the conversation up to that point into a new chat"* — ancestry-to-here, no options. **Msty's** Branch Explorer is read-only visualisation; its labels do not control model context.

**Not found, stated explicitly:** LlamaCanvas and Bonsai returned no relevant results. Flowith's edge semantics are **unverified** — its first-party page was unusable and every available claim is third-party review copy. `langchain-ai/langgraph-studio` 404s (not separately open-sourced).

<a name="hosted-products-vendor-claims-only"></a>
### Hosted products — all VENDOR CLAIM, none observed

No account, no browser: **every statement in this section is a vendor claim**, and where a first-party page could not be reached the cell reads "not addressed in retrieved first-party docs" — absence of documentation, never "no".

**Retrieval note affecting credibility:** `help.openai.com` and `www.perplexity.ai` returned **403 to every direct fetch**. Their content was retrieved through a text proxy that returns first-party bytes (verified by intact `ctfassets.net` asset URLs and matching `#h_…` anchors). `support.anthropic.com` **301-redirects to `support.claude.com`**. Three products were renamed during the period covered: NotebookLM → **"Gemini Notebook"**, Perplexity Spaces → **"Projects"**. All three renames make older third-party writing on these products unreliable — a further reason the brief's primary-source rule is correct.

| Product | Branching | Cross-conversation memory | Project scope | Inspect included context | Exclude / revoke | Export |
|---|---|---|---|---|---|---|
| **ChatGPT Projects** | ✅ "Branch in new chat" | project-only vs default, user-selectable | ✅ project instructions override global | via memory sources panel | delete file from sources; project-only memory severs outside context | ✅ ≤7 days; **not available** on Business/Enterprise/Healthcare |
| **ChatGPT memory** | n/a | ✅ chats, files, connected apps | n/a | ✅ **strongest inspection in the survey** | ⚠️ must delete *every* source | as above |
| **Claude Projects + memory** | ❓ **not addressed** — grep of full release notes Aug 2025→Aug 2026 for `branch\|fork`: **zero hits** | ✅ topic-based memory + RAG past-chat search | ✅ separate memory space per project | ✅ Topics list; past-chat **citations**; search appears as a **tool call** | ⚠️ incognito is pre-emptive only; no retroactive per-chat exclusion short of deletion | ⚠️ **cannot import into another account**; memory "export" is a prompt |
| **Gemini Gems** | not addressed | ✅ — but **explicitly excluded inside Gems** | instructions + Knowledge files | ⚠️ weak — prompt-based ("ask Gemini") | delete chats from Activity + disconnect app | ✅ Google Takeout |
| **Gemini Notebook** (ex-NotebookLM) | not addressed | notebook-scoped only | ✅ answers grounded only in your sources | ✅ **best provenance in the survey** — plus an explicit prompt-composition table | ✅ **per-source checkbox include/exclude** | not addressed in retrieved docs |
| **M365 Copilot Notebooks / Pages** | not addressed | ✅ Copilot Memory + chat-history inferences | ✅ "uses only this curated content"; chats "Move to notebook" | saved-memories list, per-item delete | delete the conversation; 30-day inference purge | not addressed as user self-serve |
| **Perplexity Projects** (ex-Spaces) | ✅ **"Forking"** (Computer only, 06/18/26) | ✅ per-project "Brain" memory | ✅ persistent shareable hub | Brain tab shows generated memory | auto/manual Brain control; no per-item revoke documented | ❌ "transferring data between accounts is not supported" |

**Three of these matter to the brief's argument and one of them undercuts it.**

**ChatGPT Projects — the brief's claim is confirmed, with a scope correction.** The article does say branching retains the original thread: *"Users can open an existing chat and continue the conversation to explore a new idea without losing the original thread"*, and branched chats appear alongside the original titled "Branch". But the article never states branching's scope; the release notes do — **September 4, 2025**: *"Hover over a message, click More actions (⋯), and select Branch in new chat… available today for all logged-in users on web."* So branching is a **general ChatGPT feature, web-only, not project-scoped**, which the brief's framing implies otherwise. Project scoping is confirmed separately: *"Project instructions only apply inside the respective project and will override your global custom instructions"*, and *"Chats cannot reference conversations outside the project."*

**ChatGPT memory has better inspection than the brief assumes — and admits its own limit.** *"You can see what sources were used to personalize a response such as custom instructions, past chats, files, and memories by tapping the book icon below the response"*, and *"Tapping on a memory in sources will open an explanation on why that memory was used."* But the same doc concedes: *"Sources… may not show every factor or source that shaped a response"* and *"memory is based on a continually updated synthesis of context from your past chats, which may be broader than what can be shown as individual items."* **This is the automatic-memory failure mode the brief's H1 is about, stated by the vendor.** Revocation is correspondingly weak: *"To fully delete something ChatGPT may know about you, you'll need to delete every source where it appears."*

**Gemini Notebook is the strongest shipped counter-example to the brief's differentiation hypothesis.** It ships user-selected sources with per-source revocation — *"you can use the checkbox on each source to include or exclude certain sources the model should use"* — grounding restricted to those sources, and **the only published prompt-composition table in the survey**: Notes *"Only when you specifically select it"*, Sources *"Always used in either the entire set or the subset you select"*, Conversation history *"Used to generate responses."* Its citations do what no OSS tool does: *"You can hover over any citation to get the full quoted text right away. If you select a citation, Gemini Notebook automatically navigates to the location of the quote."* **That is per-claim attribution, shipping, at Google scale** — and it materially weakens the per-claim-attribution gap identified above. The distinction that survives: Gemini Notebook grounds in *documents you upload*, not in *your other conversations*, and it has no edge/graph construct.

**Perplexity "Forking" is the closest shipped thing to the brief's core concept.** Changelog 06/18/26: *"Forking lets you ask a follow-up question or explore a new iteration in a fresh thread, while keeping full access to the previous thread's context and generated assets."* A directed context link between two separately-addressable conversations, shipping. Scoped to Perplexity's Computer surface and not mentioned in the Projects help articles.

**Claude:** no branching documented anywhere — a full-text grep of twelve months of release notes for `branch|fork` returns zero hits. Its memory design is notable for the brief's conflict question: *"Claude saves memory as a set of individual topics as you chat, rather than summarizing conversations after they end"*, with past-chat search surfacing *"as tool calls"* and *"citations linking back to the original chats."* The help doc's own heading **"Can I exclude a specific past chat from searches?"** is answered only with incognito mode — i.e. **pre-emptive only, no retroactive revocation**, which is precisely the brief's revocation requirement going unmet by a major vendor.

### Patents

**One directly relevant patent found, and it is recent, granted, and close.**

**US 12,561,533 B1 — "Chatbots with non-linear conversations"** ([Google Patents](https://patents.google.com/patent/US12561533B1/en)). Inventor Bastian Best; applicant Powerclaim GmbH. **Priority and filing 2025-08-25; granted 2026-02-24.** 14 claims.

Independent claim 1 covers non-destructive branching with **maintained separate contexts**:

> *"allowing the user to revisit and revise earlier parts of the conversation and non-destructively create a second conversation path separate from the first conversation path that coexists and is separate from the first conversation path… and maintaining distinct conversation contexts for the first conversation path and the second conversation path."*

**Three dependent claims cover most of the brief's proposed edge semantics:**

- **Claim 9 — user-selected context exclusion:** *"receiving a user selection to exclude selected user prompts or chatbot responses from a current conversation context; and generating a subsequent chatbot response based only on included prior user prompts and chatbot responses."*
- **Claim 6 — merge:** *"receiving a user request to merge the second conversation path into the first conversation path; generating a merged conversation context…"*
- **Claim 7 — summary-passing on merge:** *"generating the merged conversation context comprises generating an automated summary of the second conversation path and injecting the summary into a conversation context of the first conversation path."*

Claim 8 covers merge by drag-and-drop; claim 12 covers weighted synthesis across two or more user-selected paths; claim 3 covers tree display with visually distinguished branches.

**Scope read, stated carefully:** every claim is confined to paths **within one conversation in one interface**. They do **not** claim a user-created directed context link between two separate, independently-addressable conversations. But the brief's phrase *"choose whether each edge passes a summary or selected messages"* maps almost exactly onto claims 7 and 9 in the intra-conversation case. **Anyone building this should get freedom-to-operate advice; this report is not that advice.**

Retrieved and rejected as off-point: US 12,242,811 B2 (Google, authored dialogue-state graphs for bots); US 12,526,253 B1 (Wishpond, bot flow authoring); CN 116821309 B, US 2025/0112878 A1, US 12,462,095 B2 (automated context construction, no user-directed link); US 7,809,842 / US 8,001,126 / US 2006/0288107 (pre-LLM session transfer).

**Conclusion on patents: no patent found claiming user-controlled directed context links between separate conversations — and this is NOT proof of novelty.** Google Patents full text was reached only through a search engine's index rather than queried directly, and applications under 18 months old are invisible by definition. US 12,561,533 B1 (filed Aug 2025, granted Feb 2026) demonstrates that the adjacent art is active and very recent, which raises rather than lowers the probability of unpublished pending applications.

*Security and governance sources are treated in their own section below, since the findings there are structural rather than per-source.*

---

## Evidence on the hypotheses H1–H5

### H1 — Control: fewer stale/irrelevant-context errors with explicit links than automatic retrieval

**UNTESTED BY ANYONE — the single largest evidence gap.** No source in the literature compares user-controlled to automatic context selection. MemGPT designs user control out; GraphRAG's index is fully LLM-constructed; LongMemEval's four control points are all system-side; Hu et al. compare graph vs flat *automatic* construction. Zero grep hits for user-control vocabulary across all five papers.

**Partially supported on a narrower claim.** ThoughtDAG's benchmark establishes that *explicit graph pruning repairs contaminated context* (subgraph 162/162 vs source-only 152/162, first-party) and that **deleting the source alone is often insufficient** because frozen downstream replies still carry the error — a non-obvious result that directly supports the brief's concern about staleness propagation. But every condition there is a hand-specified graph transformation. **There is no automatic-retrieval arm anywhere in it.** The comparison H1 actually names has never been run.

### H2 — Provenance: users identify sources more accurately when inherited context and citations are visible

**UNTESTED, and the literature is weaker on this than the brief assumes.** Lewis et al. name provenance in the abstract as an open problem — the brief's citation is verified near-verbatim: *"providing provenance for their decisions and updating their world knowledge remain open research problems."* But **"provenance" appears exactly once in the entire paper.** There is no provenance metric, no attribution evaluation, no citation-correctness experiment. Interpretability is asserted in prose and never measured.

The asymmetry is instructive: RAG's *sibling* property, updateability, **was** measured — the index hot-swap experiment (70%/68% matched vs 12%/4% mismatched) is a genuine result. Provenance was named and left. Downstream, GraphRAG measures comprehensiveness/diversity rather than attribution correctness; Hu et al. treat interpretability as design intuition.

**The brief's own instruction — "provenance must be evaluated as an outcome, not assumed from the presence of links" — is correct and is the right lesson to carry forward.**

**On tooling, state the gap precisely, because the absolute version is false.** No *open-source* tool examined does per-claim attribution: ThoughtDAG has node-level and PDF-page provenance, Threadline has jump-to-source, and neither maps a sentence in an answer to the node that supplied it. But **Gemini Notebook ships click-to-locate per-claim citations into uploaded documents** (*"If you select a citation, Gemini Notebook automatically navigates to the location of the quote"*), and Claude surfaces *"citations linking back to the original chats."* So the gap is specifically **per-claim attribution across user-authored links between conversations** — not per-claim attribution as such, which is shipping at scale for documents.

### H3 — Efficiency: better answer quality per token than passing all prior history

**SUPPORTED for pruning, on synthetic tasks, first-party.** ThoughtDAG's Track A design isolates this properly with a `linear_all_padded` length control that separates "shorter" from "cleaner" and enforces ≤5% token parity at compile time, refusing to run otherwise. That is the right experimental design. However, the *published* pilot covers the Repair track (Track C); the branch-merge results are in the scenario suite, which the authors deliberately keep off the main leaderboard as a different evidence duty.

**Adjacent support:** GraphRAG reports 26–33% fewer context tokens at low-level community summaries and >97% at root level versus map-reduce source-text summarization — but that is a different axis (global sensemaking) and a different baseline.

**Caveat:** all of this is synthetic, English-only, exact-match, single-run at temperature 0.

### H4 — Usability cost: tolerable only for recurring or complex work

**PARTIALLY TESTED, BY ADJACENT HCI WORK, AND THE THREE INDEPENDENT READINGS DISAGREE.** This is the hypothesis where the evidence position improved most during the investigation — peer-reviewed user studies of node-graph LLM interfaces do exist, they just study *workflow* graphs rather than *conversation* graphs.

- **[AI Chains](https://doi.org/10.1145/3491102.3517582) (CHI 2022, N=20) — positive, with a named cost.** Chaining significantly improved transparency (5.4±1.3 vs 3.8±1.8, *p*=.002) and controllability (6.2±0.9 vs 4.5±1.3, *p*<.001), and reduced undos (18% vs 45%), with **no significant time penalty** (14.6 vs 12.4 min, *p*=.278). But 9 of 20 reported a steeper learning curve, 4 lost end-to-end visibility — *"how my particular change to this data entry will affect the final result"* — and 3 missed unstructured experimentation.
- **[VisCanvas](https://arxiv.org/abs/2607.21886) (2026-07, N=20) — null result.** Cognitive load and usability *"indistinguishable from current prevailing methods"* versus a chat baseline.
- **[Do Conversational Interfaces Limit Creativity?](https://arxiv.org/abs/2507.08260) (2025-07) — uneven.** Graph benefits accrue *"for users who can effectively use them."*
- **[ChainForge](https://doi.org/10.1145/3613904.3642016) (CHI 2024)** localises the cost precisely: *"the majority of usability issues revolved around the flow UI, such as needing to move nodes around to make space, connecting nodes and deleting edges"* — **raw graph mechanics, not comprehension** — yet 4.19/5 satisfaction and 18 participants wanted to use it again.

**Read together: the graph does not reliably reduce cognitive load, but it does measurably improve *transparency and controllability* — which are exactly what the brief cares about — and the cost lands on graph manipulation mechanics rather than on understanding.** That is a more favourable position for H4 than "no evidence", and it sharpens the interview protocol: measure wiring effort separately from comprehension, because prior work says they diverge.

**Still untested for conversation graphs specifically.** All four studies concern workflow/authoring graphs. ThoughtDAG's design document explicitly scopes the conversational HCI experiment out.

**Circumstantial signal on maintenance:** ThoughtDAG ships *nine* topology diagnostics (residual edges, shadow references, blind-pool breaches, pool asymmetry, long chains, open branches, collider continuations, orphan materials, load-bearing nodes) with locate-and-fix actions. **A tool does not build a static analyser for its own graphs unless real users produce malformed graphs.** Indirect evidence that the brief's research question 6 names a real problem — inference, not measurement.

### H5 — Differentiation: a gap exists only if permissions, inspection, and revocation are materially stronger

**LARGELY REFUTED, with one narrow survivor.**

- **Inspection: refuted.** ThoughtDAG ships a per-message pre-send preview with per-layer token accounting; Threadline ships a select-before-inject panel. Both predate this brief.
- **Revocation: refuted.** Delete an edge and regenerate is ThoughtDAG's headline demo, with a benchmark measuring how well it works.
- **Permissions: NOT refuted — and unoccupied by everyone.** No tool examined enforces an authorization boundary on an edge. ThoughtDAG's blind-pool diagnostic *detects* an isolation breach but does not *prevent* it, and it runs on demand rather than live. Its trust mechanism is a system-prompt instruction asking the model to weigh bracketed labels — which OWASP LLM02 states outright can be *"bypassed via prompt injection."* Three of four other repos have nothing at all; tldraw's worker forwards unvalidated client-supplied messages with no system prompt.

**The security standards leave the same hole, which raises confidence that it is real rather than an artifact of my search.** NIST AI 600-1 has zero occurrences of "trust boundar", "isolat", "segregat" or "least privilege" in 64 pages; its authorization-adjacent suggested actions are procurement-shaped (inventory third parties, add contract clauses). OWASP does supply the right principle — LLM06 #7 *"Implement authorization in downstream systems rather than relying on an LLM to decide if an action is allowed"* — but never applies it to conversations. **Nobody has specified what an enforced boundary between one user's own two chats would even mean.**

**So H5's gap narrows to two clauses: enforcement, and the per-message provenance that enforcement would need to operate on.** Everything else in the hypothesis is answered by shipped software.

---

## Answers to research questions 1–8

**1. Which jobs genuinely require context to move between independent conversations?**
**No evidence.** This requires the interview round. The brief's §2 remains necessary and its screener should be behavioural (count of chats used on one project in the last 30 days; a named concrete instance) rather than attitudinal.

**2. What does an edge mean?**
**Answered by prior art, and better than the brief frames it.** ThoughtDAG's resolution: *edges decide identity, nodes decide volume.* An edge chooses whether a source enters as conversation (solid) or as a fenced reference block (dashed), and at what depth (quote = source Q/A + ancestor-question trail; full = whole upstream transcript). How *much* of a node flows is a node property (archive, highlight-filter, collapse). One level of indirection: a reference never forwards its own references. Three of four other implementations answer this question as "nothing" — the edge is a routing line.

**3. Who should choose transmitted context — user, system, or both?**
**Unanswered, and the strongest available answer is "nobody has tested it."** Verified negative across the entire literature.

**4. Can users predict what a destination chat knows and explain why?**
**Unanswered. This is the highest-value open question and the cheapest to test**, because a mature tool already implements the thing to be tested — you can run the study against ThoughtDAG rather than building a prototype first.

**5. How should conflicts, edits, deletion, staleness, cycles, and source precedence behave?**
**Substantially answered by prior art + benchmark.** Staleness: fingerprint the upstream at generation time, normalize away view state, mark drift, inject an explicit stale marker downstream. Deletion: **source deletion alone is insufficient** — measured, 152/162 vs 162/162 for subgraph excision. Cycles: block the dashed→solid conversion that would close one. Precedence: deterministic layer order (materials → references → conversation), independent of edge creation history. **Source precedence between conflicting upstream sources remains genuinely open** — no tool resolves it, and the benchmark's finding that conflicting statements derail models in 162/162 outcomes while irrelevant asides derail them in 0/81 says conflict is the failure mode that matters.

**6. At what graph size does maintenance become worse than search or folders?**
**No measurement anywhere.** Indirect signal only: ThoughtDAG ships nine topology diagnostics and a three-tier semantic zoom, which implies the authors hit real navigability limits.

**7. Which existing products already satisfy the target job, and what evidence remains for differentiation?**
**ThoughtDAG satisfies most of it within a single canvas; Gemini Notebook satisfies the source-selection-plus-provenance half at Google scale for documents; Perplexity's "Forking" ships the cross-conversation link.** Remaining differentiation is narrow: enforcement-grade edge permissions (unoccupied by every tool *and* both security standards), per-claim cross-conversation attribution, the full three-way per-edge transform (which CTA names as an open problem in print), and cross-canvas linking. See [The differentiation gap](#the-differentiation-gap).

**8. Does the approach improve correctness, provenance, privacy control, token use, or completion time?**
- Correctness: **yes, for pruning contaminated context** (first-party, synthetic, unreproduced). Versus automatic retrieval: **untested**.
- Provenance: **untested as an outcome, by anyone, ever.**
- Privacy control: **untested**; no enforcement exists to test.
- Token use: **supported** with a proper length control in the design, though the branch-merge results are held off the main leaderboard.
- Completion time: **no data.**

---

## Security & governance findings

Threat model under examination: **(a)** chat A contains text the user pasted from an untrusted source carrying injected instructions, which now flows into chat B's prompt across a user-drawn edge; **(b)** the existence of an edge between two chats is itself metadata revealing a relationship even when message text is hidden.

Sources: [OWASP Top 10 for LLM Applications **2025**](https://genai.owasp.org/llm-top-10/) (confirmed current — every entry numbered `LLM0N:2025`; no 2026 list exists) and [NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) (July 2024, no revision suffix, not superseded).

### The headline finding: this threat model sits in a documented blind spot

**Both standards consistently assume the boundary of concern runs *between principals* — users, tenants, third parties, organizations. Neither contemplates isolation *within* one principal's own data.** This is not an inference; it is verified by exhaustive grep over the extracted primary text.

| Term | NIST AI 600-1 (64 pp.) | OWASP LLM01 |
|---|---|---|
| "trust boundar" | **0** | 1 — and only as a *red-teaming* recommendation |
| "isolat" | **0** | — |
| "segregat" | **0** | — |
| "least privilege" | **0** | — |
| "session" | **0** | 0 |
| "tenant" | **0** | 0 |
| "conversation" | 1 — unrelated (chatbot mental-health disclosure, §2.3) | 1 — Scenario #2 only |

Three specific consequences:

1. **OWASP LLM01 arguably does not name threat (a).** Indirect injection is scoped to *"input from external sources, such as websites or files."* Chat A's transcript is neither. The payload entered as **direct** input (the user pasted it) but reaches chat B **indirectly** via the edge, with no human in the loop at re-injection. OWASP has no term for this. The top-level definition is broad enough to reach it — *"prompt injections do not need to be human-visible/readable, as long as the content is parsed by the model"* — which also means collapsed or hidden UI content still counts.
2. **NIST is the better citation for threat (a).** §2.9: *"Indirect prompt injection attacks occur when adversaries remotely (i.e., without a direct interface) exploit LLM-integrated applications by injecting prompts into data likely to be retrieved."* That describes a chat A → chat B edge exactly, and is medium-agnostic where OWASP's "websites or files" is not.
3. **Threat (b) has no primary-source coverage at all.** Neither document treats the existence of a link between two data sources as itself a disclosure. NIST §2.4's *"stitching together information from disparate sources"* is about *the model inferring* PII, not about a stored graph structure revealing a relationship. NIST's provenance appendix (A.1.6) treats metadata as something you *record for* provenance, never as something whose recording is itself disclosive. **This is a defensible novelty claim — and one of the few in this report.**

### The brief's OWASP claim: verified verbatim

> *"While techniques like Retrieval Augmented Generation (RAG) and fine-tuning aim to make LLM outputs more relevant and accurate, research shows that they do not fully mitigate prompt injection vulnerabilities."* — [OWASP LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

OWASP's stronger concession, opening its mitigation section, is the more load-bearing sentence for this project:

> *"Given the stochastic influence at the heart of the way models work, it is unclear if there are fool-proof methods of prevention for prompt injection."*

That is the primary-source basis for arguing this feature needs **architectural containment rather than filtering** — and directly indicts ThoughtDAG's system-prompt-instruction approach.

### The mitigation that this architecture structurally defeats

OWASP LLM01 mitigation **#6 "Segregate and identify external content"** — *"Separate and clearly denote untrusted content to limit its influence on user prompts"* — presupposes you can *label* content as external. **An intra-user edge defeats exactly that.** Once untrusted text is pasted into chat A's transcript it is indistinguishable from user-authored text; at the moment the edge fires there is nothing left to segregate.

**This is the strongest primary-source argument in the report for capturing provenance at paste time rather than at edge-traversal time** — and it converges with the per-claim-attribution gap identified above from an entirely independent direction.

### The most on-point control in either document

[OWASP **LLM08:2025 Vector and Embedding Weaknesses**](https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/) exists and is closer to this threat model than LLM01. Mitigation **#3 "Data review for combination & classification"**:

> *"When combining data from different sources, thoroughly review the combined dataset. Tag and classify data within the knowledge base to control access levels and prevent data mismatch errors."*

That is precisely what an edge between two chats does *not* do by default. Its Scenario #1 (hidden white-on-white text in a resume steering a RAG screening system) also supplies the **admission checkpoint** principle NIST lacks: *"all input documents must be validated before they are added."*

**Note the same blind spot recurs:** LLM08 names *"Cross-Context Information Leaks"* — but scopes it to *"multi-tenant environments where multiple classes of users or applications share the same vector database."* Cross-*user*, not cross-*context-within-one-user*. Third occurrence of the same assumption.

### Where to source authorization guidance, since NIST has none

NIST's authorization-adjacent suggested actions are procurement-shaped: inventory third parties (GV-6.1-007), add contract clauses (GV-6.1-006), document data sources (MG-3.2-003). **There is no suggested action prescribing technical isolation or an authorization boundary between two data sources feeding the same model.** Use OWASP instead:

- **LLM06 #7 Complete mediation** — *"Implement authorization in downstream systems rather than relying on an LLM to decide if an action is allowed or not."* This is the correct principle if chat B can act on anything as a result of inherited content: the authorization decision must not be made by the model reading the poisoned transcript.
- **LLM08 #1 Permission and access control** — *"strict logical and access partitioning of datasets."*

Also relevant: **LLM02:2025** notes that prompt-level confidentiality restrictions *"may not always be honored and could be bypassed via prompt injection or other methods"* — so a design relying on instructing chat B not to reveal chat A's content is already ruled out by primary text.

### The strongest NIST hook: information integrity, argued from definition rather than analogy

NIST §2.8 defines high-integrity information as information that:

> *"can be linked to the original source(s) with appropriate evidence. High-integrity information is also accurate and reliable, can be verified and authenticated, has a clear chain of custody, and creates reasonable expectations about when its validity may expire."*

**A chat edge without per-message provenance severs both "linked to the original source(s)" and "clear chain of custody."** One can argue directly from NIST's own stated criteria — not by analogy — that a chat-linking feature without provenance capture produces low-integrity information *by definition*. Note also the final clause, *"reasonable expectations about when its validity may expire"*: that is staleness, which ThoughtDAG already implements and which NIST independently names as an integrity criterion.

Two NIST suggested actions are direct design requirements:

- **GV-6.1-008** — *"Maintain records of changes to content made by third parties to promote content provenance, including sources, timestamps, metadata."*
- **MP-3.4-001** — *"Evaluate whether GAI operators and end-users can accurately understand content lineage and origin."* This is the user-facing counterpart, and it is essentially **task T2 of the interview protocol above**, prescribed by NIST.

**Scope caveat, stated so the report does not overclaim:** NIST's provenance theme is oriented almost entirely to distinguishing AI-generated from human-generated content (watermarking, deepfake detection). The sentence *"Data provenance refers to tracking the origin and history of input data"* supports extending it to authorship provenance within a transcript — but it is an extension, not something NIST prescribes.

**A further gap:** every NIST human-review action (MG-3.2-006, MG-3.2-008, MG-4.1-007) addresses review of ***generated*** content or organizational monitoring. **None prescribes human review of ***retrieved*** content before it enters a prompt** — which is exactly the moment that matters here.

### What the tools actually do, measured against the above

- ThoughtDAG **recognises** the risk in code comments — link snapshots carry source + capture date because *"web content drifts, and fetched text is an injection surface — keep it clearly fenced."*
- Its mitigation is **labelling plus a system-prompt instruction** asking the model to judge trust from bracketed markers. Measured against OWASP: this is an attempt at mitigation #6 (segregate and identify), defeated by the paste-time labelling problem, backed by a prompt-level control that LLM02 and LLM01 both state can be bypassed. **It is the weakest class of defence for this risk, and OWASP says so in the primary text.**
- **No tool examined implements a trust tier, sanitisation pass, or authorization check on cross-edge content.** tldraw's worker is the extreme case: it forwards a client-supplied `ModelMessage[]` to Gemini with no validation and no system prompt — mediation is entirely absent.
- **Metadata (threat b):** ThoughtDAG's read-only share links compress the *entire graph* into the URL. Excellent for portability and no-server privacy — and it means the graph *shape*, i.e. which conversations are connected to which, travels with any shared link. Since no standard treats this as a disclosure, no tool guards against it. The event log is explicitly metadata-only and exports as CSV.

---

## The differentiation gap

Stated as narrowly as the evidence permits:

**There is no differentiation gap in the interaction model.** User-controlled context graphs with per-edge semantics, pre-send inspection, revoke-and-regenerate, staleness propagation, and isolation checking are implemented and shipping in ThoughtDAG, and the broad concept is implemented ~20 times over on GitHub. A visual graph alone is not a position — the brief's own decision criteria already say so.

**Two gaps survive, both narrow:**

1. **Enforcement-grade permissions on an edge.** Every tool treats an edge as a *selector* over content. None treats it as an *authorization boundary* — a rule consulted independently of relevance, that holds even when the upstream content instructs the model otherwise, and that can be tested. This is unoccupied across all prior art examined and is the only candidate for a defensible position. It is also *hard*, and OWASP states in primary text why: *"it is unclear if there are fool-proof methods of prevention for prompt injection."*

   **This gap is corroborated from an independent direction by the standards themselves.** Both OWASP and NIST assume the boundary of concern runs between *principals* — verified by zero grep hits for "trust boundar", "isolat", "segregat", "least privilege", "session" or "tenant" across all 64 pages of NIST AI 600-1. Even OWASP LLM08's *"Cross-Context Information Leaks"* is scoped to multi-tenancy. **Intra-principal compartmentalisation — one user, two of their own conversations that should not see each other — is unaddressed by the security literature and unimplemented by every tool examined.** Two independent bodies of work leaving the same hole is stronger evidence of a real gap than either alone.

2. **Per-claim attribution across user-authored conversation links.** Stated precisely, because the absolute version is false: Gemini Notebook already ships click-to-locate per-claim citations *into uploaded documents*, and Claude cites *source chats*. What no tool does is map a sentence in an answer back to the upstream **node reached over a user-drawn link**. Three lines of evidence converge here, which is why it has been promoted above cross-canvas linking: (a) H2 is untested by anyone, and RAG named provenance once and never measured it; (b) OWASP LLM01 mitigation #6 requires segregating untrusted content, which is *impossible at edge-traversal time* if provenance was not captured at paste time; (c) NIST §2.8 defines high-integrity information as having *"a clear chain of custody"* and NIST MP-3.4-001 explicitly asks whether end-users *"can accurately understand content lineage and origin."* **This is the feature most likely to produce a measurable outcome difference, and the one with the clearest standards mandate.**

3. **The full per-edge transform — verbatim / selected messages / summary — is unclaimed across ~40 verified items.** This is narrower and better-evidenced than I expected. ThoughtDAG implements two of the three (`quote` and `full`) but no per-edge summarisation. CTA implements a binary and **names the missing knob as an open problem in print**: *"selective relevance filtering and compression are not yet implemented."* Flow editors have summarising memory (Flowise) but bound to a session key, never to an edge. ChainForge has a "Past Conversation" edge that carries the full history with no options. LibreChat has three selection modes but only as a one-shot copy at fork time. **Nobody has shipped a reusable, inspectable, revocable edge property that chooses among all three.**

4. **Cross-conversation (separately stored) linking.** ThoughtDAG's edges live within one canvas. Real, but an unbuilt feature with an obvious implementation rather than a defensible position — DAG-chat's backend would already accept it, and Perplexity's "Forking" already ships something adjacent.

**Note the shape of what survives, because it is the opposite of the brief's emphasis.** Gaps 1 and 2 are *provenance-and-enforcement plumbing*. Gap 3 is a single edge property. **The visual graph — the part the brief foregrounds — is the part that is most thoroughly anticipated**, by ~20 GitHub projects, seven Obsidian plugins since 2023, a granted patent, and a published formalisation.

**Two caveats that narrow gap 2 further.** Google's Gemini Notebook already ships click-to-locate per-claim citations into source documents, and a granted patent (US 12,561,533 B1, claims 7 and 9) covers summary-injection-on-merge and user-selected message exclusion within a single conversation. Neither closes the gap for *cross-conversation* attribution, but both mean the surrounding space is occupied and moving.

**"Not found" is an open result.** The absence of an enforcement-grade implementation is not proof that none exists — my search covered GitHub, arXiv, first-party product documentation and the sources named in the brief. It did not cover closed-source enterprise products, non-English repositories, or anything unindexed.

---

## Recommendation

**NARROW.** Not stop, not MVP.

**MVP is not an available conclusion.** The brief requires all five decision criteria to be met. Three of them — participant demonstration of the job, prototype outcome improvement, and 80% task success on prediction and revocation — require humans and code that Phase 1 cannot produce. Only one criterion is decidable now:

> *"The prior-art review identifies a specific unmet interaction or enforcement gap; a visual graph alone is insufficient."*

**This criterion is met, but only just, and only on the enforcement clause.** The interaction gap is closed by prior art. The enforcement gap is real and unoccupied.

**Not stop, because** the two independent negatives converge on a genuinely open question rather than a settled one: the literature has never evaluated user-controlled context selection in either direction, and the most advanced implementation says its own human question is unanswered. Stopping would treat "unstudied" as "refuted."

**Narrow to this:** *enforced, inspectable context permissions between separately stored conversations, with per-claim attribution* — and validate it with the two cheap tests below before writing product code. Explicitly drop: the visual-graph-as-differentiator framing, the biology metaphor (already out of scope, and the naming concern in the brief stands), and any graph-database ambition.

**Criteria that remain unadjudicated:** participant count demonstrating the job; explicit-graph outcome improvement without worsening task time; 80% unaided task success on prediction and revocation; and the deletion/authorization/injection architecture tests.

**Two things to do before any product code is written.**

1. **Get freedom-to-operate advice on US 12,561,533 B1.** Its claims 7 and 9 — summary injection on merge, and user-selected exclusion of messages from context — map closely onto the brief's *"choose whether each edge passes a summary or selected messages"*, in the intra-conversation case. The patent was filed 2025-08 and granted 2026-02, so the adjacent art is active and recent; applications under 18 months old are invisible by definition. This report is not legal advice and did not attempt an FTO analysis.
2. **Reframe the pitch away from the interface.** Every artifact-level claim in this space is anticipated. What survives is provenance capture at paste time, enforcement, and one unclaimed edge property. A narrative built on "visual graph of chats" competes with ~20 GitHub projects, seven Obsidian plugins, a patent and a paper. A narrative built on "your context has a chain of custody and the boundary is enforced, not suggested" competes with nobody — including, per the grep evidence, the security standards.

---

## Ready-to-run plan for the parts requiring humans or code

### A. Interview + usability protocol (brief §2), revised by Phase-1 evidence

**The key revision: do not build a paper prototype.** The brief assumed the artifact needed inventing. It does not. Run the sessions **against ThoughtDAG** — MIT-licensed, free tier covers every feature, desktop app keeps all participant data local, and it ships an append-only metadata-only event log exportable as CSV for objective action counts instead of video coding. This is cheaper, faster, and produces higher-grade evidence than a paper prototype, because participants interact with a real system whose assembled context is *objectively checkable* against `buildContext`.

**Recruit 8–12** people who in the last 30 days split one piece of work across ≥3 separate AI chats. Behavioural screener:
- "In the last month, how many separate AI chats did you use for one project?" (≥3 to qualify)
- "Describe the last time you had to re-explain something to a new chat." (must produce a specific instance; reject if not)
- Never ask whether the idea sounds useful.

**45-minute session, screen-shared, recorded with consent:**

1. **(8 min) Retrospective.** Reconstruct one real multi-chat episode. Capture chats involved, what was re-pasted, what was lost, what workaround was used. Code for *cost*: time, rework, wrong answer shipped.
2. **(10 min) Baseline observation.** A synthesis task in their normal tool, thinking aloud. Record time, copy-paste events, and whether they verify the source of any claim.
3. **(15 min) Tool session.** ThoughtDAG pre-loaded with a canvas **the participant did not build**: three independent research chains plus an empty synthesis node. Give no explanation of the model first. Each task scored pass/fail *without coaching*:
   - **T1 Predict** — "Before you press send, tell me exactly which of these chains the answer will use." Scored against the actual `partitionContext` output. Objectively checkable.
   - **T2 Attribute** — "This claim in the answer: which chain did it come from?"
   - **T3 Revoke** — "Chain B is out of date. Make the answer stop using it."
   - **T4 Recover** — "You linked the wrong chain. Undo that without losing your other work."
   - **T5 Maintain** — open a 40-node canvas built by someone else: "find where the pricing decision was made."
4. **(7 min) Cost probe.** "Would you have built this graph yourself for the task in step 1? What would you have skipped?" Look for unprompted use of controls, not stated intent.
5. **(5 min)** Wrap, consent re-confirm, withdrawal path.

**Decision thresholds:** ≥5 participants independently demonstrate the same costly job; ≥80% unaided success on T1 and T3. **T1 is the disconfirming test** — if users cannot predict included context in a tool that already shows them a per-message preview, the concept's premise fails and no amount of interface work rescues it. Run T1 first.

**Two design constraints imposed by the HCI literature, not invented here.**

- **Measure wiring effort separately from comprehension.** ChainForge found usability cost concentrated in graph *mechanics* (*"needing to move nodes around… connecting nodes and deleting edges"*) while comprehension was fine; AI Chains found the reverse pattern for a subset (transparency improved, but 4 of 20 lost end-to-end visibility). Collapsing these into one "usability" score would reproduce a known confound. Use the event log for mechanics, T1/T2 for comprehension.
- **Add a fourth condition: Gemini Notebook.** It ships per-source include/exclude and click-to-locate citations, which is T2 and T3 done well without any graph. If participants succeed at T2/T3 there and fail on the canvas, the graph is the problem, not the concept. This costs one extra 10-minute block and is the sharpest available control.

**Ethics:** informed consent; ThoughtDAG desktop keeps project data on the participant's machine; redact quotes; 90-day retention; withdrawal by email.

### B. Three-condition prototype (brief §3), narrowed by Phase-1 evidence

**Do not rebuild the pollute/propagate/prune experiment.** It exists, is public, and re-scores offline:

```bash
git clone https://github.com/chenxiachan/thoughtdag
BENCH_SUITE=pilot-v1 node benchmark/tools/score.mjs pilot-v1-nemotron-nano-9b   # zero API calls
```

Adding an endpoint is one `envelope.json`. **Do this first** — it converts the strongest external evidence in this report from first-party claim to independently reproduced, for roughly zero cost.

**What that benchmark does NOT contain, and what the prototype must therefore add:**

- **(a) An automatic-retrieval condition.** Every existing condition is a hand-specified graph transformation. There is no "let a retriever pick from all eligible chats" arm anywhere in the prior art. **Without it, H1 is untested by anyone.** This is the single highest-value experiment available.
- **(b) A human arm** — who chooses the graph operation, and do they choose correctly?
- **(c) An adversarial arm** — injected instructions crossing an edge.

**Minimal build (~3 days, no new dependencies beyond `sqlite3` and one provider SDK):**

- **Corpus:** 20–30 task families as flat JSON transcripts. Seed from the benchmark's 9 families; extend with 3 conflicting-fact, 3 superseded-decision, 3 irrelevant-chat, 3 injection items.
- **Store:** SQLite + FTS5. **No vector database** — the brief's own scope rule. Add embeddings only if FTS5 recall is *measured* insufficient.
- **Conditions**, one model pinned at temperature 0, exact model id recorded per row:
  - `ISOLATED` — destination prompt is its own turns only.
  - `AUTOMATIC` — FTS5 BM25 top-k over all chats in the workspace, k tuned once on a held-out split.
  - `EXPLICIT` — only user-linked chats eligible; per-edge mode ∈ {full, selected-messages, summary}; assembled prompt printed verbatim before send. **The three-way mode is the point**: CTA implements only a binary and states *"selective relevance filtering and compression are not yet implemented"*, so a measured comparison of all three per-edge modes is unpublished work, not a reimplementation.
- **Assembly:** one function, `build_prompt(dest_id, mode) -> messages`, plus `hash(messages)` per run. Dump every assembled prompt to disk. Borrow the benchmark's discipline: *a result without its trace is not a result.*
- **Scoring:** exact-match/numeric where possible, **no LLM judge**; attribution scored against a gold claim→source map; injection arm scored by deterministic canary check.
- **Metrics:** correctness; unsupported-claim rate; attribution precision/recall; stale-fact adoption; input tokens; latency; canary-emission rate per condition.
- **Analysis:** pre-register expected direction per metric and the stopping rule. Pair by family — the benchmark's own correction applies (depth and variant rows are repeated measures, not independent n; use McNemar on paired outcomes, not Fisher exact).

**Decision value:** if `EXPLICIT` does not beat `AUTOMATIC` on correctness *or* canary-emission rate, the concept has no measured justification and should stop. If it beats it on canary rate specifically, that isolates the enforcement gap — the only surviving differentiation candidate — and points directly at what to build.

---

## Search log

All searches conducted 2026-08-27. "Disposition" records what happened, not what I hoped for.

| # | Query / URL | Site / database | Disposition |
|---|---|---|---|
| 1 | `https://github.com/chenxiachan/thoughtdag` | GitHub API (`gh api repos/`) | 200. 289★, 27 forks, created 2026-02-17, pushed 2026-08-25, MIT, TypeScript |
| 2 | `repos/chenxiachan/thoughtdag/releases` | GitHub API | 200. 31 releases; v0.3.31 published 2026-08-25 |
| 3 | `git clone --depth 1` × 4 repos | GitHub | All succeeded |
| 4 | `src/store/context-builder.ts` (326 lines) | Local clone | Read in full. **Primary evidence for edge semantics** |
| 5 | `src/lib/graph.ts` — `partitionContext` | Local clone | Read in full. Three-layer partition, `contextDepth` |
| 6 | `src/lib/diagnostics.ts` | Local clone | Read. Blind-pool breach + pool asymmetry = isolation checking |
| 7 | `grep -rn "contextDepth" src/` | Local clone | 6 hits; per-edge depth is a first-class property |
| 8 | `grep -rn "buildContext(" src/` | Local clone | 14 call sites; preview path confirmed at `FollowUpInput.tsx:70` |
| 9 | `grep -rn "injection\|untrusted" src/ -i` | Local clone | 3 hits, all comments/labelling. **No enforcement** |
| 10 | `grep -rn "projectId" src/types.ts src/lib/graph.ts src/store/context-builder.ts` | Local clone | **Zero hits — edges cannot span canvases** |
| 11 | `benchmark/DESIGN.md`, `STATUS.md`, `README.md` | Local clone | Read in full. Pre-registration + withdrawn claims |
| 12 | `chenxiachan.github.io/thoughtdag/research/context-repair-pilot-v2/` | First-party site | 200. 9 endpoints, 1,485 runs, scope limits stated |
| 13 | `search/repositories?q=branching+chat+canvas+LLM` | GitHub API | 200, 8 results |
| 14 | `search/repositories?q="branching"+"canvas"+chat+in:description` | GitHub API | 200, ~20 relevant results, mostly 2026. **Field is saturated** |
| 15 | `gh search repos "graph chat LLM canvas"` (and 3 variants) | GitHub CLI | Returned empty; superseded by the API queries above |
| 16 | `arxiv.org/abs/2310.08560` (MemGPT) | arXiv | 200. Packer et al. Grep for user-control vocabulary: **zero hits** |
| 17 | `gh api repos/cpacker/MemGPT` | GitHub API | **Redirects to `letta-ai/letta`** — project renamed to Letta. 24,449★ |
| 18 | `arxiv.org/abs/2005.11401` (RAG) | arXiv | 200. Brief's claim verified near-verbatim. "Provenance" occurs **once** |
| 19 | `microsoft/research/project/graphrag/overview/` | Microsoft Research | 200 but **thin/JS-rendered**. One usable sentence; substance taken from arXiv instead |
| 20 | `arxiv.org/abs/2404.16130` (GraphRAG) | arXiv | 200. Auto-extraction confirmed; indexing cost only as wall-clock |
| 21 | `gh api repos/microsoft/graphrag` | GitHub API | 200. Active, 35,696★, v3.1.2 (2026-08-21) |
| 22 | `proceedings.iclr.cc/.../d813d324...pdf` (LongMemEval) | ICLR proceedings | **200 — the brief's hash URL works.** ICLR 2025. Grep for user-control: **zero hits** |
| 23 | `aclanthology.org/2026.acl-long.1232/` | ACL Anthology | **200 — real, verified.** Hu et al., ACL 2026 pp. 26758–26782 |
| 24 | `aclanthology.org/2026.acl-long.1232.pdf` | ACL Anthology | 200. Abstract quoted from PDF (landing page carries no abstract) |
| 25 | `raw.githubusercontent.com/tldraw/tldraw/main/apps/docs/content/starter-kits/branching-chat.mdx` | GitHub raw | **200 — did not 404** |
| 26 | `search/repositories?q=branching-chat+org:tldraw` | GitHub API | Found `tldraw/branching-chat-template` (`tldraw/branching-chat` is 404) |
| 27 | `MessageNode.tsx` `handleSend`, `nodePorts.tsx` `getAllConnectedNodes` | Local clone | Read. **Ordering defect on merge topologies identified** |
| 28 | `convex/agentActions.ts`, `chats.ts`, `schema.ts` | Local clone | Read. **`parentAgentMessageId` never reaches `streamText`** |
| 29 | `grep zermindAgent.createThread` | Local clone | Exactly one hit (`chats.ts:281`) — one thread per chat |
| 30 | `backend/api/routes/chat.py` | Local clone | Read. `topological_sort_subdag` — only correct merge ordering in the set |
| 31 | `src/utils/rag.ts`, `recall-helpers.ts` | Local clone | Read. `formatRAGPrompt`; select-before-inject preview |
| 32 | `tiktoken\|countTokens\|estimateToken` across 4 repos | Local clones | **Zero hits in all four.** Only ThoughtDAG counts tokens |
| 33 | `stale\|invalidat\|regenerate` across 4 repos | Local clones | **Zero context-related hits in all four** |
| 34 | `help.openai.com/en/articles/10169521` + release notes | OpenAI Help | **403 to direct fetch and curl.** Retrieved via text proxy (first-party bytes verified by intact asset URLs/anchors). Brief's claim confirmed with a scope correction |
| 34b | `help.openai.com/.../8590148-memory-faq` vs `.../11146739` | OpenAI Help | Both serve **identical bodies** (7420 vs 7449 bytes, delta = URL-string length). Server-side merge. **No standalone "Reference chat history" article found** despite Projects doc naming that toggle |
| 34c | `support.anthropic.com` | Anthropic | **301 → `support.claude.com`** |
| 34d | grep `branch\|fork` over Claude release notes Aug 2025–Aug 2026 | support.claude.com | **Zero hits.** No branching documented |
| 34e | `support.google.com/gemininotebook/answer/16179559` etc. | Google | 200. **NotebookLM renamed "Gemini Notebook."** Per-source checkbox + prompt-composition table |
| 34f | `support.microsoft.com` Copilot Notebooks/Pages | Microsoft | 200 (constructed Pages slug 404'd; correct slugs found by search) |
| 34g | grep `fork` over `perplexity.ai/changelog` | Perplexity | **"Forking", entry 06/18/26.** Spaces renamed "Projects" |
| 35 | 7 patent queries (conversation graph / node-based context propagation / directed edge inheritance / cross-session transfer / branching thread context selection / linked conversation context source / context-inheritance DAG) | patents.google.com | **US 12,561,533 B1 found** (filed 2025-08-25, granted 2026-02-24). 6 others retrieved and rejected as off-point |
| 36 | `genai.owasp.org/llmrisk/llm01-prompt-injection/` | OWASP | 200, no redirect. Title `LLM01:2025 Prompt Injection`. RAG/fine-tuning claim **verified verbatim** |
| 37 | `genai.owasp.org/llm-top-10/` | OWASP | 200. **2025 list confirmed current**; no 2026 list exists |
| 38 | `genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/` | OWASP | 200. Prompt-level confidentiality restrictions stated bypassable |
| 39 | `genai.owasp.org/llmrisk/llm062025-excessive-agency/` | OWASP | 200. "Complete mediation" mitigation extracted |
| 40 | `genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/` | OWASP | 200. **Exists.** Most on-point control in either document |
| 41 | `nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf` | NIST | 200, 64 pp., July 2024, no revision suffix, not superseded |
| 42 | grep `trust boundar\|isolat\|segregat\|least privilege\|session\|tenant` | NIST 600-1 extracted text | **0 hits for all six.** Blind spot verified, not inferred |
| 43 | grep `conversation` | NIST 600-1 extracted text | 1 hit, unrelated (§2.3 chatbot mental-health disclosure) |
| 44 | 20 arXiv API queries via `export.arxiv.org/api/query` | arXiv | Saturation by query ~16. **Note: `http://` returns an empty body silently — must use `https://`** |
| 45 | `cat:cs.HC AND all:"conversation branching"` | arXiv | **0 results** |
| 46 | `all:"graph-based chat interface"` | arXiv | **0 results — the phrase is not used in the literature** |
| 47 | ar5iv full text: 2110.01691, 2203.06566, 2305.11473, 2305.11483, 2309.09128 | arXiv/ar5iv | All read. AI Chains and PromptChainer are **two distinct CHI 2022 papers** (full paper vs Extended Abstracts) |
| 48 | PDF extraction, arXiv 2603.21278 (CTA) | arXiv | **Closest published formalisation.** Names per-edge filtering/compression as unimplemented |
| 49 | Vendor docs read as raw markdown from their own docs repos | Langflow, Flowise, Rivet, n8n, Dify, LangChain, Prompt Flow, Visual Blocks, comfyui_LLM_party | Primary source; avoids JS-rendered pages. **Flowise repo is ARCHIVED** |
| 50 | Obsidian Canvas AI plugin sweep | GitHub | 7 plugins verified, earliest 2023. **Zero per-edge transforms** |
| 51 | LlamaCanvas; Bonsai | GitHub | **Not found** — no relevant results |
| 52 | Flowith edge semantics | flowith.io | **Unverified** — first-party page returned title only; all available claims are third-party review copy |
| 53 | `langchain-ai/langgraph-studio`; `caretplugin.ai` | GitHub / DNS | **404**; **dead DNS**. Corrections: `comfyui_LLM_party` is `heshengtao/`, not VectorSpaceLab; Luminate is CHI 2024 and is not a node-graph chat tool |

---

## Annotated bibliography

**Primary — source code (observed behaviour).**

- **ThoughtDAG**, Xia Chen, MIT. <https://github.com/chenxiachan/thoughtdag> — The closest prior art. `src/store/context-builder.ts` and `src/lib/graph.ts` are the load-bearing files; `src/lib/diagnostics.ts` implements isolation checking; `benchmark/DESIGN.md` is a genuine pre-registration and `benchmark/STATUS.md` records withdrawn claims after audit. Cited throughout.
- **DAG-chat**, ZM-BAD, MIT. <https://github.com/ZM-BAD/DAG-chat> — `backend/api/routes/chat.py` contains the only correct topological merge ordering in the set. README claims match code.
- **tldraw branching-chat-template**. <https://github.com/tldraw/branching-chat-template> — Starter kit. `client/nodes/types/MessageNode.tsx` + `client/nodes/nodePorts.tsx` show the ordering defect on merges. README claims Durable Objects the worker does not contain.
- **Zermind**, okikeSolutions, MIT. <https://github.com/okikeSolutions/zermind> — `convex/agentActions.ts` shows branching that does not affect model context. Material README mismatch.
- **Threadline**, terra901, Apache-2.0. <https://github.com/terra901/Threadline> — Miscategorised by the brief (capture+RAG extension, not a DAG chat app), but has the best provenance and portability in the OSS set.

**Primary — papers.**

- **Packer et al., "MemGPT: Towards LLMs as Operating Systems"** (arXiv 2310.08560, v2 2024-02-12). <https://arxiv.org/abs/2310.08560> — Two-tier memory with self-directed paging. Relevant chiefly as a *negative*: it explicitly excludes user control. Project now shipping as Letta (<https://github.com/letta-ai/letta>).
- **Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"** (arXiv 2005.11401, v4 2021-04-12). <https://arxiv.org/abs/2005.11401> — The brief's citation is verified. Note the asymmetry: updateability is measured (§4.5 index hot-swap), provenance is named once and never measured. This is the paper's most useful lesson for this project.
- **Edge et al., "From Local to Global: A Graph RAG Approach to Query-Focused Summarization"** (arXiv 2404.16130, v2 2025-02-19). <https://arxiv.org/abs/2404.16130> — Auto-extracted entity graph for global sensemaking. Different axis from cross-conversation memory; do not cite as support for user-drawn edges. Indexing cost published only as wall-clock.
- **Wu et al., "LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory"** (ICLR 2025). <https://proceedings.iclr.cc/paper_files/paper/2025/file/d813d324dbf0598bbdc9c8e79740ed01-Paper-Conference.pdf> — Five abilities: information extraction, multi-session reasoning, temporal reasoning, knowledge updates, abstention. The 30–60% drop is measured *relative to oracle retrieval*, not raw capability — cite carefully. All control points system-side.
- **Hu et al., "Does Memory Need Graphs? A Unified Framework and Empirical Analysis for Long-Term Dialog Memory"** (ACL 2026, pp. 26758–26782). <https://aclanthology.org/2026.acl-long.1232/> — **The title is rhetorical; the answer is conditionally yes.** Graph beats flat on retrieval with the gap widening at scale; loses when Value=Key or the extractor is weak. Real headline: unreported implementation details swamp the graph/no-graph axis. Code: <https://github.com/AvatarMemory/UnifiedMem>.

**Primary — standards.**

- **OWASP Top 10 for LLM Applications 2025.** <https://genai.owasp.org/llm-top-10/> — Confirmed current edition. Four entries bear on this project: **LLM01 Prompt Injection** (<https://genai.owasp.org/llmrisk/llm01-prompt-injection/>) verifies the brief's RAG/fine-tuning claim verbatim and, more usefully, concedes that fool-proof prevention may not exist; its mitigation #6 "segregate and identify external content" is the one this architecture structurally defeats. **LLM02 Sensitive Information Disclosure** states prompt-level confidentiality restrictions are bypassable by injection. **LLM06 Excessive Agency** supplies "complete mediation" — authorization must not be delegated to the model reading the content. **LLM08 Vector and Embedding Weaknesses** (<https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/>) is the closest control in either document; its mitigation #3 and Scenario #1 give the admission-checkpoint principle NIST lacks.
- **NIST AI 600-1, "Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile"** (July 2024). <https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf> — 12 GAI risks; §2.9 Information Security gives the better indirect-injection definition for this threat model; §2.8 Information Integrity is the strongest hook, because its own criteria ("linked to the original source(s)", "clear chain of custody", "reasonable expectations about when its validity may expire") are what an unprovenanced edge severs. Suggested actions GV-6.1-008 and **MP-3.4-001** ("evaluate whether end-users can accurately understand content lineage and origin") are direct design requirements — the latter is essentially task T2 of the interview protocol, prescribed by NIST. **Caveat:** NIST's provenance theme is oriented to synthetic-vs-human content detection; applying it to authorship provenance within a transcript is a defensible extension, not a NIST prescription.
- **Negative result, verified by grep rather than asserted:** neither document addresses trust boundaries between a single user's own conversations, and neither treats a stored link between two data sources as itself a disclosure.

**Primary — HCI literature (peer-reviewed; the strongest evidence on usability cost).**

- **Wu et al., "AI Chains: Transparent and Controllable Human-AI Interaction by Chaining LLM Prompts"** (CHI 2022). <https://doi.org/10.1145/3491102.3517582> · <https://arxiv.org/abs/2110.01691> — The best evidence for H4. Significant gains in transparency and controllability with no time penalty, against a named learning-curve and loss-of-end-to-end-visibility cost. Edge = plain data flow; control comes from editing intermediate layers.
- **Wu et al., "PromptChainer: Chaining Large Language Model Prompts through Visual Programming"** (CHI 2022 Extended Abstracts). <https://doi.org/10.1145/3491101.3519729> — A *separate* paper from AI Chains, on the graph authoring tool. Relevant mental-model finding: with branching logic *"it became unclear how the entities fed into the classifier mapped to the original input node."*
- **Jiang et al., "Graphologue"** (UIST 2023). <https://doi.org/10.1145/3586183.3606737> — Converts a single response into a node-link diagram. **Edges are extracted entity relations, not context conduits** — the user never authors what flows.
- **Suh et al., "Sensecape"** (UIST 2023). <https://doi.org/10.1145/3586183.3606756> — Multilevel sensemaking canvas. Notably, *semantic dive does not inherit prior conversation* — users copy/paste across layers manually.
- **Arawjo et al., "ChainForge"** (CHI 2024). <https://doi.org/10.1145/3613904.3642016> · <https://github.com/ianarawjo/ChainForge> (3,027★) — Two things matter here: the **"Past Conversation" edge input** is the closest named-edge precedent found anywhere (and carries full history with no options), and it is one of only two tools in ~40 with a genuine pre-run prompt preview.
- **"Conversation Tree Architecture"** (arXiv 2603.21278, 2026-03-22). <https://arxiv.org/abs/2603.21278> — **The most useful positioning citation in this report.** An independent formalisation of this exact concept that implements only a binary transform and states in print that *"selective relevance filtering and compression are not yet implemented."* Design-space paper, no user study. Filed cs.CL, so cs.HC searches miss it.
- **VisCanvas** (arXiv 2607.21886, 2026-07) and **"Do Conversational Interfaces Limit Creativity?"** (arXiv 2507.08260, 2025-07) — the two dissenting readings on cognitive load. Both necessary to avoid overclaiming from AI Chains alone.
- **JumpStarter** (arXiv 2410.03882, 2024-10) — not a graph, but the best statement of the underlying problem: *"users still have to identify and supply the right context at each decision point, regardless of how much the model can store."*

**Patents.**

- **US 12,561,533 B1, "Chatbots with non-linear conversations"** (Powerclaim GmbH; filed 2025-08-25, granted 2026-02-24). <https://patents.google.com/patent/US12561533B1/en> — Claims non-destructive branching with maintained distinct contexts (cl. 1), user-selected exclusion of messages from context (cl. 9), merge (cl. 6), and **summary injection on merge (cl. 7)**. Scoped to paths within one conversation. Get freedom-to-operate advice; this report is not that advice.

**Vendor documentation (all VENDOR CLAIM — no observed behaviour possible).**

- **ChatGPT Projects** <https://help.openai.com/en/articles/10169521> and release notes <https://help.openai.com/en/articles/6825453> — 403 to direct fetch; retrieved via text proxy. Brief's claim confirmed; branching is a general web-only feature, not project-scoped.
- **ChatGPT memory FAQ** <https://help.openai.com/en/articles/8590148> — Best inspection in the survey, with a vendor-stated limit that is itself evidence for the brief's H1.
- **Claude memory and projects** <https://support.claude.com> (note: `support.anthropic.com` 301-redirects here) — No branching documented in twelve months of release notes. Retroactive per-chat exclusion unavailable.
- **Gemini Notebook** (formerly NotebookLM) <https://support.google.com/gemininotebook/answer/16179559> and <https://support.google.com/notebooklm/answer/16269187> — **The strongest shipped counter-example in the survey**: per-source include/exclude checkboxes, click-to-locate citations, and the only published prompt-composition table.
- **Microsoft 365 Copilot Notebooks / Pages**, **Perplexity Projects** (formerly Spaces) and its changelog entry of 06/18/26 introducing **"Forking"** — the closest shipped analogue to a directed context link between two separately-addressable conversations.

**Search artifacts.** GitHub API repository searches, 2026-08-27, documented in the search log above. ~20 further node-canvas branching-chat repositories identified at description level and **not source-verified** — given that two of four verified repos had README claims their code does not support, treat that list as an upper bound on capability.
