# Spec: Trend & Emergence Analysis System

**Status:** Proposed
**Priority:** P2 (Enhancement)
**Created:** 2026-01-09
**Last Updated:** 2026-02-21

---

## Problem

Users need to identify emerging topics and trends in their research digests across time. Currently, the toolkit only aggregates content without temporal analysis or pattern detection.

## Goals

Build a stateful trend analysis system that:
1. Identifies trending topics using LDA (Latent Dirichlet Allocation)
2. Detects emerging terms using TF-IDF analysis
3. Tracks topic evolution over configurable time windows (default: 7 days)
4. Maintains incremental state for continuous monitoring
5. Generates actionable reports on landscape shifts

## Non-Goals

- Real-time analysis (batch processing is sufficient)
- LLM-based summarization (use classical NLP techniques)
- Interactive visualization dashboard (terminal/markdown output only)

## Proposed Solution

### Architecture

```
Scraped Content → Text Extraction → Preprocessing →
LDA Topic Modeling → Temporal Analysis → TF-IDF Emergence →
Report Generation
```

### Components

**1. Text Extraction Layer**
- Read markdown files from `research_digest/`
- Extract metadata (source, date, title)
- Generate extractive summaries for long documents

**2. Preprocessing Pipeline**
- Tokenization (sentence + word level)
- Stopword removal (English + domain-specific)
- Lemmatization (WordNet)
- N-gram detection (bigrams, trigrams)

**3. LDA Topic Modeling**
- Use `gensim` library (implements Gibbs sampling)
- Default: 10-20 topics, configurable
- Coherence metrics for quality assessment
- Per-document topic distributions

**4. Temporal Analysis**
- 7-day rolling windows (configurable)
- Trend velocity metrics (growth/decline rate)
- Burstiness detection (current vs historical frequency)
- Topic evolution tracking across windows

**5. TF-IDF Emergence Detection**
- Compare recent window vs historical corpus
- Identify new terms with high TF-IDF scores
- Semantic clustering of emerging terms
- Anomaly detection for sudden term appearance

**6. Report Generation**
- Rich console tables (trending topics, emerging terms)
- Markdown reports for Obsidian integration
- Status classification: stable, growing, declining, emerging, fading

### Database Schema

Extend `research_digest_state.db` with:
- `analysis_runs` - Track each analysis execution
- `document_corpus` - Indexed document metadata
- `lda_topics` - Topic models per run
- `document_topics` - Document-topic mappings
- `trend_metrics` - Temporal trend data
- `semantic_clusters` - Grouped emerging terms

### Configuration

Add to `research_config.yaml`:
```yaml
trend_analysis:
  enabled: false
  window_days: 7
  num_topics: 15
  min_document_frequency: 3
  max_document_frequency: 0.8
  emergence_threshold: 2.0
```

### CLI Interface

```bash
# Run analysis on latest digest
./rdt/digest.py --analyze-trends

# Run analysis on specific date range
./trend_analysis.py --start 2026-01-01 --end 2026-02-21

# View latest trends
./trend_analysis.py --report
```

## Implementation Plan

**Phase 1: Foundation (Week 1)**
- [ ] Database schema extensions
- [ ] Text extraction and preprocessing pipeline
- [ ] Unit tests for preprocessing

**Phase 2: Topic Modeling (Week 2)**
- [ ] LDA integration with gensim
- [ ] Coherence scoring and model validation
- [ ] Store topic models in database

**Phase 3: Temporal Analysis (Week 3)**
- [ ] Rolling window implementation
- [ ] Velocity and burstiness metrics
- [ ] Topic evolution tracking

**Phase 4: Emergence Detection (Week 4)**
- [ ] TF-IDF scoring for time windows
- [ ] Semantic clustering of terms
- [ ] Emergence threshold tuning

**Phase 5: Reporting (Week 5)**
- [ ] Rich console output with tables
- [ ] Markdown report generation
- [ ] Integration with main digest workflow

## Success Metrics

- [ ] Successfully identifies trending topics in test corpus
- [ ] Detects known emerging terms (validated manually)
- [ ] Analysis completes in < 2 minutes for 100 documents
- [ ] Reports are actionable (user can understand trends without ML knowledge)
- [ ] 80%+ test coverage for new modules

## Open Questions

1. **LDA hyperparameters:** How to choose α and β? (Proposal: use perplexity-based tuning)
2. **Emergence threshold:** What TF-IDF ratio indicates "emerging"? (Proposal: 2x historical mean)
3. **Topic stability:** How to track topic evolution across runs? (Proposal: word overlap similarity)
4. **User feedback:** Should users be able to label topics for future runs? (Future enhancement)

## Dependencies

**New Python packages:**
- `gensim` - LDA topic modeling
- `spacy` - NLP preprocessing (lemmatization, POS tagging)
- `scikit-learn` - TF-IDF, clustering
- `nltk` - Stopwords, tokenization

## References

- Original implementation plan: `docs/archive/TREND_ANALYSIS_IMPLEMENTATION_PLAN.md`
- Gensim LDA docs: https://radimrehurek.com/gensim/models/ldamodel.html
- Topic coherence metrics: Röder et al. (2015)
