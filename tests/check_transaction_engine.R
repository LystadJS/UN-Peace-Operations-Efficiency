#!/usr/bin/env Rscript
# Test only synthetic fixture records; no inference about actual UN expenditures.
arg <- commandArgs(trailingOnly = TRUE)
if (length(arg) != 1L) stop("Usage: Rscript tests/check_transaction_engine.R OUTPUT_DIRECTORY")
pair <- read.csv(file.path(arg[[1]], "pair_reconciliation.csv"), stringsAsFactors = FALSE)
cases <- read.csv(file.path(arg[[1]], "case_summary.csv"), stringsAsFactors = FALSE)
stopifnot(nrow(pair) == 4L, nrow(cases) == 3L)
stopifnot(sum(pair$matched_one_to_one) == 3L)
stopifnot(sum(!pair$matched_one_to_one) == 1L)
stopifnot(all(cases$independently_audited_pairs == 0L))
stopifnot(all(cases$realized_net_savings_usd == "not_estimated"))
stopifnot(all(pair$incremental_net_savings_usd == "not_estimated"))
stopifnot(all(pair$document_status[pair$matched_one_to_one] == "synthetic_test_match"))
cat("SYNTHETIC R LEDGER ACCEPTANCE TESTS PASSED: 3 matches, 1 unmatched, 0 savings claims.\n")
