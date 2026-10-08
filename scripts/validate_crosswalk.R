#!/usr/bin/env Rscript
# Validate the source-linked research crosswalk without additional R packages.

args <- commandArgs(trailingOnly = TRUE)

root <- if (length(args) > 0L) {
  normalizePath(args[[1L]], mustWork = TRUE)
} else {
  normalizePath(".", mustWork = TRUE)
}

read_data <- function(name, key) {
  path <- file.path(root, "data", paste0(name, ".csv"))

  if (!file.exists(path)) {
    stop("Missing required dataset: ", path, call. = FALSE)
  }

  x <- read.csv(
    path,
    check.names = FALSE,
    stringsAsFactors = FALSE,
    na.strings = character(),
    fileEncoding = "UTF-8"
  )

  if (!(key %in% names(x)) || anyDuplicated(names(x)) ||
      !nrow(x) || anyDuplicated(x[[key]]) ||
      anyNA(x) || any(trimws(as.matrix(x)) == "")) {
    stop("Invalid CSV structure or duplicate primary key: ", path, call. = FALSE)
  }

  x
}

names_and_ids <- c(
  source_manifest = "source_id",
  functional_inventory = "function_id",
  mandate_inventory = "mandate_id",
  deliverable_inventory = "deliverable_id",
  financial_guardrails = "record_id",
  crosswalk = "crosswalk_id",
  un80_register = "reform_id",
  candidate_validation = "candidate_id",
  non_overlap_controls = "control_id",
  quality_issues = "issue_id",
  evidence_links = "evidence_id"
)

data <- Map(read_data, names(names_and_ids), unname(names_and_ids))
names(data) <- names(names_and_ids)

expect <- function(test, message) {
  if (!isTRUE(all(test))) {
    stop(message, call. = FALSE)
  }
}

functions <- data$functional_inventory
crosswalk <- data$crosswalk
deliverables <- data$deliverable_inventory
candidates <- data$candidate_validation
evidence <- data$evidence_links

expect(
  crosswalk$dppa_function_id %in% functions$function_id &
    startsWith(crosswalk$dppa_function_id, "F") &
    crosswalk$dpo_function_id %in% functions$function_id &
    startsWith(crosswalk$dpo_function_id, "G"),
  "Unresolved crosswalk function IDs"
)

allowed <- c(
  "documented_shared_structure",
  "documented_joint_process",
  "planned_coordination",
  "candidate_overlap",
  "complementary_different_roles",
  "distinct_mandates"
)

expect(crosswalk$classification %in% allowed, "Unexpected classification")
expect(
  crosswalk$reform_id == "-" |
    crosswalk$reform_id %in% data$un80_register$reform_id,
  "Unresolved reform IDs"
)

expect(
  as.integer(crosswalk$dppa_pdf_page) >= 1L &
    as.integer(crosswalk$dppa_pdf_page) <= 134L &
    as.integer(crosswalk$dpo_pdf_page) >= 1L &
    as.integer(crosswalk$dpo_pdf_page) <= 67L,
  "Crosswalk PDF page out of range"
)

split_refs <- function(x) {
  if (x == "-") character(0L) else strsplit(x, ";", fixed = TRUE)[[1L]]
}

expect(
  all(unlist(lapply(crosswalk$deliverable_ids, split_refs)) %in%
        deliverables$deliverable_id),
  "Unknown linked deliverable"
)

expect(
  all(unlist(lapply(candidates$crosswalk_ids, split_refs)) %in%
        crosswalk$crosswalk_id),
  "Candidate references missing crosswalk"
)

expect(
  candidates$savings_status %in% c("not_estimated", "not_applicable"),
  "Unsubstantiated quantified savings"
)

for (id in crosswalk$crosswalk_id) {
  pair <- evidence[evidence$object_type == "crosswalk" &
                     evidence$object_id == id, , drop = FALSE]

  expect(
    nrow(pair) == 2L && setequal(pair$side, c("DPPA", "DPO")),
    paste("Crosswalk pair missing evidence links:", id)
  )
}

expect(
  as.integer(deliverables$actual_2025) >= 0L &
    as.integer(deliverables$planned_2027) >= 0L,
  "Invalid numeric deliverable value"
)

cat("VALIDATION PASSED\n")
for (name in names(data)) {
  cat(name, ": ", nrow(data[[name]]), " records\n", sep = "")
}
cat("Scope: structure and references only; not independent budget or mandate verification.\n")
