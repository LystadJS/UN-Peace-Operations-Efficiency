#!/usr/bin/env Rscript
# Audit 2026/27 approved peacekeeping mission-maintenance amounts (base R only).
# Data are USD thousands; inclusive GA appropriations also include support/UNLB/RSCE.
args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args)) args[[1]] else "."
file <- file.path(root, "data", "ga_mission_reconciliation.csv")
if (!file.exists(file)) stop("Missing GA reconciliation file: ", file)
d <- read.csv(file, stringsAsFactors = FALSE, check.names = FALSE)
req <- c("mission_id", "ga_approved_maintenance_usd_thousands",
  "sg_proposal_usd_thousands", "adopted_minus_proposed_usd_thousands",
  "ga_appropriation_usd_thousands", "ga_adoption_status")
if (!all(req %in% names(d))) stop("Missing required column(s)")
if (nrow(d) != 6 || anyDuplicated(d$mission_id)) stop("Expected six unique mission rows")
if (!all(d$ga_adoption_status == "verified_in_uploaded_operative_resolution")) stop("Approval not verified")
difference <- d$ga_approved_maintenance_usd_thousands - d$sg_proposal_usd_thousands
if (anyNA(difference) || !all(abs(difference - d$adopted_minus_proposed_usd_thousands) <= 0.12)) {
  stop("Variance mismatch")
}
if (abs(sum(d$ga_approved_maintenance_usd_thousands) - 4028188) > 0.12) {
  stop("Approved maintenance subtotal mismatch")
}
out <- data.frame(
  mission = d$mission_id,
  SG_proposal_USDm = d$sg_proposal_usd_thousands / 1000,
  GA_maintenance_USDm = d$ga_approved_maintenance_usd_thousands / 1000,
  GA_minus_SG_USDm = difference / 1000
)
print(out, row.names = FALSE, digits = 10)
cat("Total GA maintenance minus SG proposal (US$m): ", sprintf("%+.4f", sum(difference)/1000), "\n", sep = "")
cat("Difference is a funding decision, NOT additional savings. SPM 2027 addenda remain unreconciled.\n")
