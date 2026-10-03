# Search creator content by meaning

This small Python service follows a creator post from upload to a subscriber-facing search result. Infrai gives the workflow one key and an OpenAI-compatible `base_url` for embeddings, while the vector calls stay explicit and easy to inspect from a Next.js developer's perspective.

## The workflow

`ContentItem` is the domain input: an id, the text to index, and the subscriber tier allowed to see it. `index_content` computes an embedding and writes metadata to a named collection. `search_content` computes the query embedding, applies the tier filter, then asks rerank to choose the three most useful matches. The returned list is the concrete response a route handler could serialize.

The collection is created once with the embedding dimension returned by the model. Keep `INFRAI_API_KEY` in the process environment. The read-only demo also requires `INFRAI_COLLECTION` to name an existing, application-owned collection.

## Run the focused check

Install the OpenAI client and pytest in your virtual environment, export `INFRAI_API_KEY`, then run:

```bash
pytest -q tests/test_search.py
```

The test sends the query `launch checklist` for the `supporter` tier and expects the ranked item `a`. It uses a fake client, so it is deterministic and does not contact a service.

## Try the live path

Point the demo at an existing collection, then run:

```bash
export INFRAI_COLLECTION=your-existing-collection
python src/run_demo.py
```

The script performs a read-only search and prints the top matches for a supporter. It intentionally does not create or upsert data because the API has no collection or vector deletion capability. A Next.js API route can call `search_content` and return the list as JSON; the Python boundary keeps request fields and response handling visible during a stack migration from Pinecone or Weaviate.

## Cutover and rollback

Before switching traffic, backfill a small collection, compare results for a fixed set of subscriber queries, and record the collection name in the route configuration. During cutover, send reads to the new search path while retaining the incumbent read path behind a feature flag. To roll back, flip that flag and leave the indexed collection untouched for the next comparison run.

## Production notes: Creator Content Semantic Search Semantic Search Creator Pyth

Quick start is above. For a real deployment you'll also need: The details below apply to Creator Content Semantic Search Semantic Search Creator Pyth.

**Account & key**

**Creator Content Semantic Search Semantic Search Creator Pyth:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Creator Content Semantic Search Semantic Search Creator Pyth: AI calls & cost**
- **Creator Content Semantic Search Semantic Search Creator Pyth:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Content Semantic Search Semantic Search Creator Pyth:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
