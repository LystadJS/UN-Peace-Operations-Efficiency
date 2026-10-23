# Priority-case dataset semantic review

**C01–C03 scoped review, 23 October 2026.** Eleven retained datasets were read at their actual row grain. This supplement preserves the original 324-dataset audit and does not authenticate UN primary text or certify complete operational populations.

| Dataset | Rows / reviewed key | Grain and interpretation |
| --- | --- | --- |
| [transaction_control_baseline.csv](../../data/transaction_control_baseline.csv) | 12 / `control_id` | One published budget/arrangement control, not one transaction. Published amounts have distinct embedded-efficiency, internal-allocation, prior-comparator and category-delta classes; rows cannot be summed. |
| [transaction_evidence_requests.csv](../../data/transaction_evidence_requests.csv) | 18 / `request_id` | One legacy requested evidence package; not a dispatched message or received record. linked_controls is a semicolon-separated many-to-many relation; received_status=not_provided is missing evidence, not a negative finding. |
| [transaction_sources.csv](../../data/transaction_sources.csv) | 12 / `source_id` | One retained document or official-page source description. Source claims and locators are transcriptions; IDs do not authenticate primary text or turn proposals into adopted requirements. |
| [transaction_validation_cases.csv](../../data/transaction_validation_cases.csv) | 3 / `case_id` | One umbrella transaction-audit case summary. case_id is RSCE/UNIFIL_UNSCOL/BINUH_UNSOH, not roadmap C01/C02/C03; zero verified pairs is an evidence count, not zero waste. |
| [rsce_workforce_model_vs_post_actions.csv](../../data/rsce_workforce_model_vs_post_actions.csv) | 9 / `line_id` | One model component, subtotal, proposed post action or reassignment. Only WF01–WF03 form the WF04 model subtotal; WF05–WF09 have different populations and cannot be netted into it. |
| [spm_2027_embedded_efficiencies.csv](../../data/spm_2027_embedded_efficiencies.csv) | 31 / `efficiency_id` | One initiative already priced into the calendar-2027 SG proposal. An estimate of an embedded measure is neither a new incremental project benefit nor an observed saving. |
| [public_opportunity_register.csv](../../data/public_opportunity_register.csv) | 18 / `opportunity_id` | One public research opportunity linked to legacy candidate/evidence IDs. parent_candidate_id uses the legacy candidate namespace; it must not join directly to roadmap Cxx case IDs. |
| [ga_adopted_directives.csv](../../data/ga_adopted_directives.csv) | 15 / `directive_id` | One retained resolution-paragraph directive transcription. Repository authority classification is retained, not newly authenticated; mission_id and linked_candidate_id are not unique keys. |
| [spm_2027_mission_budget.csv](../../data/spm_2027_mission_budget.csv) | 36 / `spm_id` | One SPM mission/mandate budget entity with multiple annual measures. Personnel table2 includes multiple categories; no year-to-year subtraction is a verified efficiency or payroll finding. |
| [public_finance_nodes.csv](../../data/public_finance_nodes.csv) | 24 / `finance_id` | One financial control total, component, memo or comparator. Parent and child nodes overlap; memo and transfer nodes cannot be treated as independent expenses or benefits. |
| [public_finance_edges.csv](../../data/public_finance_edges.csv) | 21 / `edge_id` | One directed inclusion/comparability relationship between finance nodes. can_sum_child_into_parent is qualified by relationship and inclusion_note; never sum all graph nodes. |

## Results and decision implications

All eleven selected row keys are populated and unique. All 38 expanded request/control memberships resolve, all 21 finance-graph endpoints resolve, and four embedded-efficiency references match after multiplying USD-thousands by 1,000. These checks establish repository correspondence, not observed delivery or evidence authenticity.

The twelve budget/arrangement controls all lack transaction document IDs and all say transaction verification has not occurred. All eighteen legacy evidence packages remain not provided; each of the three case summaries records zero verified pairs. Their `0` values count verified pairs and do not measure zero waste. Unknown monetary claims remain `not_estimated`, not numeric zero.

RSCE modeled FTE, proposed post actions and payroll reassignments remain different measures. The -25/-10/+44 model reconciles to its +9 subtotal; neither +44 proposed transaction posts nor 17 reassignments is an extra model component. Unique post records are still required.

UNIFIL–UNSCOL controls UF01–UF03 link to EFF019/EFF026/EFF029; their 394,000 + 36,900 + 7,200 USD is the 438,100 USD proposal already embedded in the baseline. Haiti BH01 links to EFF022 at 1.4 million USD; BH02 is a broader 4 million USD proposed internal reimbursement. The two Haiti amounts cannot be netted as like-for-like service costs.

The five priority entity labels map to canonical identities; the JSON lists exact IDs. Legacy candidate labels such as C12 and roadmap labels such as C02 occupy separate namespaces. URL-only joins remain unapproved because documents and aliases span multiple claims and locators.

No candidate advances and no benefit is recognized. Close the remaining public-source interpretation questions through the priority source packets, then obtain authorized asset/invoice/post/workload/outcome records at their physical or transactional grain.

[Machine-readable observations, missing-value counts and input hashes](../../data/priority_cases/dataset_semantic_review.json). Regenerate with `python -B scripts/validate_priority_semantics.py --write`; verify with `--check`.
