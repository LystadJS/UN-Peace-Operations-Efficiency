#!/usr/bin/env Rscript
# Report budget changes without confusing proposals with audited savings.
# All amounts are in thousands of US dollars and cover 1 July 2026 to 30 June 2027.
args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args)) args[[1]] else "."
path <- file.path(root, "data", "mission_budget_register.csv")
if (!file.exists(path)) stop("Missing ", path)
b <- read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
required <- c("mission_id", "apportioned_2025_26_gross", "proposed_2026_27_gross",
              "proposal_minus_prior_apportionment", "budget_status")
if (!all(required %in% names(b))) stop("Missing required columns")
if (anyDuplicated(b$mission_id)) stop("Duplicate mission IDs")
if (any(is.na(b$apportioned_2025_26_gross)) || any(is.na(b$proposed_2026_27_gross))) {
  stop("Missing mission budgets")
}
if (!all(b$budget_status == "SG_proposal_not_appropriation")) {
  stop("Budget status may not be treated as appropriation")
}
delta <- b$proposed_2026_27_gross - b$apportioned_2025_26_gross
if (!all(abs(delta - b$proposal_minus_prior_apportionment) < 0.11)) {
  stop("Proposal comparison does not reconcile")
}
print(b[, c("mission_id", "apportioned_2025_26_gross",
             "proposed_2026_27_gross", "proposal_minus_prior_apportionment")],
      row.names = FALSE)
cat("\nCombined six-mission proposal change (not net savings; non-representative subset): ",
    sprintf("%.1f", sum(delta)), " thousand USD\n", sep = "")
cat("Source caveat: annual SG gross proposals; GA appropriation and interfund allocations not reconciled.\n")
