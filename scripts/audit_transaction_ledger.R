#!/usr/bin/env Rscript
# Reconcile UN mission asset, bill, settlement and chargeback records.
# Internal records must remain outside the public repository.
# Matching proves consistency of supplied records, NOT additional net savings.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) {
  stop("Usage: Rscript scripts/audit_transaction_ledger.R INPUT_LEDGER.csv OUTPUT_DIRECTORY", call. = FALSE)
}
input <- args[[1L]]
dest <- args[[2L]]
if (!file.exists(input)) stop("Ledger not found: ", input)
if (normalizePath(dirname(input)) == normalizePath(file.path(getwd(), "data"))) {
  warning("Live ledger should not be placed in publicly versioned data/")
}
x <- read.csv(input, stringsAsFactors = FALSE, check.names = FALSE, na.strings = c("", "NA"))
required <- c("record_id", "case_id", "event_type", "object_key",
              "source_entity", "destination_entity", "period_start", "period_end",
              "event_date", "amount_usd", "quantity", "document_ref", "evidence_status")
if (!all(required %in% names(x))) stop("Missing fields: ", paste(setdiff(required, names(x)), collapse = ", "))
if (!nrow(x)) stop("Empty ledger: no actual events were supplied.")
if (anyNA(x$record_id) || anyDuplicated(x$record_id)) stop("Missing or repeated record IDs.")
case_ids <- c("UNIFIL_UNSCOL", "BINUH_UNSOH", "RSCE")
event_pairs <- list(
  asset = c("asset_release", "asset_receipt"),
  billing = c("client_payable", "provider_receivable"),
  settlement = c("client_payment", "provider_settlement"),
  allocation = c("allocation_debit", "allocation_credit")
)
allowed <- unlist(event_pairs, use.names = FALSE)
if (anyNA(x$case_id) || !all(x$case_id %in% case_ids)) stop("Unknown case ID.")
if (anyNA(x$event_type) || !all(x$event_type %in% allowed)) stop("Unknown event type.")
if (anyNA(x$object_key) || any(!nzchar(trimws(x$object_key)))) stop("Missing object key.")
if (anyNA(x$document_ref) || any(!nzchar(trimws(x$document_ref)))) stop("Document reference required.")
if (anyNA(x$evidence_status) ||
    !all(x$evidence_status %in% c("synthetic", "unverified", "internal_signed"))) {
  stop("Evidence status must be synthetic, unverified or internal_signed.")
}
if (anyNA(x$amount_usd) || any(!is.finite(x$amount_usd)) || any(x$amount_usd < 0)) {
  stop("amount_usd must be finite and nonnegative.")
}
if (anyNA(x$source_entity) || anyNA(x$destination_entity)) stop("Missing entity in ledger.")
for (field in c("period_start", "period_end", "event_date")) {
  original <- x[[field]]
  parsed <- as.Date(original, format = "%Y-%m-%d")
  if (anyNA(parsed) || any(format(parsed, "%Y-%m-%d") != original)) {
    stop("Invalid YYYY-MM-DD date in ", field)
  }
}
if (any(as.Date(x$period_start) > as.Date(x$period_end))) stop("Reversed service periods.")
if (any(is.na(x$quantity[x$event_type %in% event_pairs$asset]))) {
  stop("Asset movements require quantity.")
}
if (any(x$quantity[x$event_type %in% event_pairs$asset] <= 0)) {
  stop("Asset movement quantity must be positive.")
}
lookup <- setNames(rep(names(event_pairs), lengths(event_pairs)), allowed)
x$event_group <- unname(lookup[x$event_type])
x$pair_key <- paste(x$case_id, x$event_group, x$object_key,
                    x$period_start, x$period_end, sep = "||")
groups <- split(seq_len(nrow(x)), x$pair_key)
results <- lapply(groups, function(ix) {
  d <- x[ix, , drop = FALSE]
  typ <- d$event_group[[1]]
  expected <- event_pairs[[typ]]
  first <- d[d$event_type == expected[[1]], , drop = FALSE]
  second <- d[d$event_type == expected[[2]], , drop = FALSE]
  one_to_one <- (nrow(first) == 1L && nrow(second) == 1L && nrow(d) == 2L)
  quant_ok <- if (typ == "asset") {
    one_to_one && abs(first$quantity - second$quantity) < 1e-8
  } else {
    one_to_one && abs(first$amount_usd - second$amount_usd) < 0.01
  }
  entity_ok <- one_to_one &&
    identical(first$source_entity, second$source_entity) &&
    identical(first$destination_entity, second$destination_entity)
  aligned <- one_to_one && quant_ok && entity_ok
  evidence <- if (aligned && all(d$evidence_status == "internal_signed")) {
    "matched_user_attested_internal_documents"
  } else if (aligned && all(d$evidence_status == "synthetic")) {
    "synthetic_test_match"
  } else if (aligned) {
    "matched_but_evidence_unverified"
  } else {
    "unmatched_or_conflicting"
  }
  data.frame(
    case_id = d$case_id[[1]], pair_type = typ, object_key = d$object_key[[1]],
    start_date = d$period_start[[1]], end_date = d$period_end[[1]],
    record_count = nrow(d),
    matched_one_to_one = aligned,
    document_status = evidence,
    amount_usd = if (one_to_one) first$amount_usd[[1]] else NA_real_,
    quantity = if (one_to_one && typ == "asset") first$quantity[[1]] else NA_real_,
    incremental_net_savings_usd = "not_estimated",
    stringsAsFactors = FALSE
  )
})
pairs <- do.call(rbind, results)
pairs <- pairs[order(pairs$case_id, pairs$pair_type, pairs$object_key), , drop = FALSE]
summary <- data.frame(
  case_id = case_ids,
  supplied_records = vapply(case_ids, function(i) sum(x$case_id == i), integer(1)),
  consistent_pairs = vapply(case_ids, function(i)
    sum(pairs$case_id == i & pairs$matched_one_to_one), integer(1)),
  mismatched_pairs = vapply(case_ids, function(i)
    sum(pairs$case_id == i & !pairs$matched_one_to_one), integer(1)),
  internal_document_pairs_attested = vapply(case_ids, function(i)
    sum(pairs$case_id == i &
        pairs$document_status == "matched_user_attested_internal_documents"), integer(1)),
  independently_audited_pairs = 0L,
  additional_addressable_cost_usd = "not_estimated",
  realized_net_savings_usd = "not_estimated",
  stringsAsFactors = FALSE
)
dir.create(dest, recursive = TRUE, showWarnings = FALSE)
if (!dir.exists(dest)) stop("Could not create output directory.")
write.csv(pairs, file.path(dest, "pair_reconciliation.csv"), row.names = FALSE, na = "")
write.csv(summary, file.path(dest, "case_summary.csv"), row.names = FALSE)
print(summary, row.names = FALSE)
cat("Pairs consistently matched:", sum(pairs$matched_one_to_one), "\n")
cat("Independent financial verification: NOT PERFORMED by record matching alone.\n")
cat("Incremental net savings: NOT ESTIMATED; counterfactual and risk review still required.\n")
