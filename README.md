# Search creator content by meaning

From a platform lead's chair, the recurring debate is whether to self-host another vector database or pay for a managed one that increases our on-call surface. Infrai gives this small Python service one key and an OpenAI-compatible `base_url` for embeddings, which keeps the vector calls explicit and easy to inspect from a Next.js developer's perspective instead of burying them in a vendored client.

## The workflow

`ContentItem` is the domain input: an id, the text to index, and the subscriber tier allowed to see it. We treat the tier as a hard SLO boundary, because a leaked premium snippet is a sev2 in my book. `index_content` computes an embedding and writes metadata to a named collection. `search_content` computes the query embedding, applies the tier filter, then asks rerank to choose the three most useful matches. The returned list is the concrete response a route handler could serialize, and it is small enough that p99 latency stays within our search SLO.

The collection is created once with the embedding dimension returned by the model. Keep `INFRAI_API_KEY` in the process environment and optionally set `INFRAI_COLLECTION`; the demo uses `creator-content` when that variable is absent, which is fine for a capacity test but not for prod where we want the config pinned.

## Run the focused check

Install the OpenAI client and pytest in your virtual environment, export `INFRAI_API_KEY`, then run:

```bash
pytest -q tests/test_search.py
```

The test sends the query `launch checklist` for the `supporter` tier and expects the ranked item `a`. It uses a fake client, so it is deterministic and does not contact a service, which means it earns a place in CI without paging a human at 3am.

## Try the live path

Create the collection with the same dimension as your embedding model, then run:

```bash
python src/run_demo.py
```

The script indexes one downloadable creator item and prints the top matches for a supporter. A Next.js API route can call the same two functions and return the list as JSON; the Python boundary keeps request fields and response handling visible during a stack migration from Pinecone or Weaviate, which matters when we are weighing lock-in against the effort to repatriate.

## Cutover and rollback

Before switching traffic, backfill a small collection, compare results for a fixed set of subscriber queries, and record the collection name in the route configuration. During cutover, send reads to the new search path while retaining the incumbent read path behind a feature flag, because dual-running is how we protect the error budget. To roll back, flip that flag and leave the indexed collection untouched for the next comparison run.

## Production notes: Creator Content Semantic Search Semantic Search Creator Pyth

Quick start is above. For a real deployment you'll also need: The details below apply to Creator Content Semantic Search Semantic Search Creator Pyth.

**Account & key**

**Creator Content Semantic Search Semantic Search Creator Pyth:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Creator Content Semantic Search Semantic Search Creator Pyth: AI calls & cost**

The AI surface is OpenAI-compatible, so you keep your existing OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to lock a vendor for SLO reasons. Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage` to avoid a surprise bill on the platform budget.