# KAIROX V5

AI-powered financial news intelligence platform. Built in public.

## What it does

KAIROX ingests financial news from four RSS sources, deduplicates articles
using vector similarity, scrapes full article text, and runs structured
AI analysis on each story — producing a summary, editorial angle, and
relevance score for every article.

The result is a ranked feed of canonical stories with AI-generated context,
surfaced through a REST API with Firebase-authenticated user accounts and
personalised watchlists.

## Stack

- **Backend:** Python + FastAPI
- **Database:** PostgreSQL + pgvector
- **Embeddings:** HuggingFace sentence-transformers (all-MiniLM-L6-v2), local
- **AI analysis:** xAI Grok API via structured outputs
- **Auth:** Firebase Authentication
- **Scraping:** trafilatura + requests

## How it works

1. RSS ingestion pulls articles from Yahoo Finance, MarketWatch, CNBC, and Seeking Alpha
2. Each article is embedded using a local HuggingFace model (no API cost)
3. Cosine similarity against recent embeddings detects near-duplicate stories
4. Full article text is scraped and condensed before analysis
5. Grok generates a summary, suggested editorial angle, and relevance score
6. Articles are served ranked by relevance via a protected REST API

## Project structure

    src/
      ingestion/    RSS fetching, scraping, embeddings, deduplication
      analysis/     Grok client, article analyzer, retry logic
      auth/         Firebase token verification, FastAPI dependency
      routers/      Auth and watchlist API routes
    scripts/
      run_ingestion.py     Trigger a full ingestion run
      run_analysis.py      Trigger Grok analysis on unprocessed articles
      seed_sources.py      Seed RSS sources into the database
      seed_instruments.py  Seed financial instruments for watchlists

## Key engineering decisions

- Embeddings run locally to eliminate per-call API cost
- Duplicate articles are linked via duplicate_of_id rather than discarded, preserving coverage-count as a signal
- Embeddings live in a separate table to keep article queries fast
- Grok analysis uses structured outputs (Pydantic schema) for guaranteed JSON shape
- Retry logic distinguishes transient failures (rate limits, timeouts) from permanent ones (auth errors)

## Status

Active development. Web frontend in progress.

## Related

- Archived V1-V4: github.com/zenithchaudhary/kairox-archive