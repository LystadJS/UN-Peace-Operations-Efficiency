# Portfolio overlap graph — I03

The [machine-readable graph](../data/portfolio/overlap_graph.json) preserves each [benefit pool](../data/portfolio/benefit_pools.json) as a hyperedge linking all its normalized interventions, including singleton pools. A derived pair projection supports inspection; it does not replace the pool boundary or count as independent evidence. Co-membership indicates potential shared cost objects that need reconciliation, rather than actual duplicate expenditure or a removable service.

Nodes retain explicit source references and separate alias namespaces. `CASE02` maps to roadmap case `C02`, while its legacy candidate references are C12/C07. A legacy C02 reporting investigation is a different object. Join through the recorded source path and identifier, never a matching C label alone.

The Lebanon transition pool links CASE02 asset effects with CASE13 residual liabilities. Other shared pools connect HQ administration, training, regional workflows and source preparation. A proposed change cannot claim the whole pool: unique economic effects, time periods, compatible scenarios, attributable marginal changes and full-system costs remain necessary. The graph allows no additive benefit aggregate, records null verified benefits and proves no actual duplicate costs.

Run `python -B scripts/build_overlap_graph.py --write` to regenerate and `--check` to verify. Input and producer SHA256 hashes identify the exact graph basis. `python -B tests/check_overlap_graph.py` checks namespace separation, retained hyperedges, shared transition costs and rejection of broken memberships. Apply the [cost-accounting standard](cost_accounting_standard.md) before any benefit recognition.
