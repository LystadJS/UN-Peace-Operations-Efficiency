#!/usr/bin/env Rscript
# Descriptive accounting for authorized local V10 instruments; no causal or savings claims.
# This script does not verify institutional authority or start a trial.

summarize_v10_workload <- function(workload_file, batches_file, output_dir) {
  fail <- function(message) stop(message, call. = FALSE)
  load_csv <- function(path, required) {
    if (!file.exists(path)) fail(paste("Missing input:", path))
    x <- read.csv(path, colClasses = "character", na.strings = "", check.names = FALSE,
                  stringsAsFactors = FALSE, fileEncoding = "UTF-8")
    if (!all(required %in% names(x))) fail(paste("Missing fields in", path))
    x
  }
  need_w <- c("segment_id", "batch_id", "actor_code", "office_code", "mode", "stage",
              "start_utc", "end_utc", "active_minutes", "record_status", "minute_basis")
  need_b <- c("batch_id", "case_id", "phase", "scope_hash", "input_snapshot_hash",
              "normal_output_status", "shadow_output_status", "normal_time_capture_complete",
              "shadow_time_capture_complete", "common_time_capture_complete", "source_equivalent",
              "task_equivalent", "language_equivalent", "review_equivalent",
              "prior_exposure_normal", "prior_exposure_shadow", "contamination", "expected_task_roster_ref")
  w <- load_csv(workload_file, need_w)
  b <- load_csv(batches_file, need_b)
  if (anyDuplicated(w$segment_id) || anyDuplicated(b$batch_id)) fail("Duplicate segment or batch identity")
  if (anyNA(w$segment_id) || anyNA(b$batch_id)) fail("Missing identity")
  if (any(!w$batch_id %in% b$batch_id)) fail("Unregistered workload batch")
  if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)
  if (file.exists(file.path(output_dir, "workload_summary.csv"))) fail("Refusing to overwrite prior readout")
  if (nrow(b) == 0L) {
    if (nrow(w)) fail("Workload without batch manifest")
    writeLines("NOT_RUN: empty instruments; no operational observations or effect estimate.",
               file.path(output_dir, "STATUS.txt"))
    return(invisible(data.frame()))
  }
  if (any(!b$case_id %in% c("SP08P1", "SP09P1"))) fail("Unknown case")
  if (any(!b$phase %in% c("public_replay", "authorized_shadow"))) fail("Substitution or unknown phase not in V10")
  for (field in c("scope_hash", "input_snapshot_hash")) {
    if (anyNA(b[[field]]) || any(!grepl("^[0-9a-f]{64}$", b[[field]]))) fail("Missing/invalid frozen hash")
  }
  flags <- c("normal_time_capture_complete", "shadow_time_capture_complete", "common_time_capture_complete",
             "source_equivalent", "task_equivalent", "language_equivalent", "review_equivalent", "contamination")
  for (field in flags) if (anyNA(b[[field]]) || any(!b[[field]] %in% c("true", "false", "unknown"))) fail("Invalid tri-state flag")
  for (field in c("normal_output_status", "shadow_output_status")) {
    if (anyNA(b[[field]]) || any(!b[[field]] %in% c("complete", "partial", "failed", "not_started"))) fail("Invalid output status")
  }
  modes <- c("normal", "shadow", "common", "setup", "evaluation")
  if (anyNA(w$mode) || any(!w$mode %in% modes)) fail("Unknown accounting mode")
  if (anyNA(w$actor_code) || anyNA(w$office_code)) fail("Missing local actor/office code")
  if (anyNA(w$record_status) || any(!w$record_status %in% c("observed", "estimated", "missing"))) fail("Invalid capture status")
  minutes <- suppressWarnings(as.numeric(w$active_minutes))
  missing <- w$record_status == "missing"
  if (any(missing & !is.na(minutes)) || any(!missing & (is.na(minutes) | !is.finite(minutes) | minutes < 0))) fail("Missing time is not zero; recorded time must be finite and nonnegative")
  parse_utc <- function(x) {
    present <- !is.na(x)
    if (any(present & !grepl("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$", x))) fail("UTC timestamps must be explicit ISO Z values")
    out <- as.POSIXct(x, format = "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")
    if (any(present & is.na(out))) fail("Invalid timestamp")
    out
  }
  start <- parse_utc(w$start_utc); end <- parse_utc(w$end_utc)
  timed <- !is.na(start) & !is.na(end)
  if (any(w$record_status == "observed" & !timed)) fail("Observed time needs start and end")
  elapsed <- as.numeric(difftime(end, start, units = "mins"))
  if (any(timed & (elapsed < 0 | (!is.na(minutes) & minutes > elapsed + 1e-8)))) fail("Time exceeds exclusive segment or reversed interval")
  for (actor in unique(w$actor_code)) {
    idx <- which(w$actor_code == actor & timed)
    idx <- idx[order(start[idx])]
    if (length(idx) > 1L && any(as.numeric(start[idx[-1L]]) < cummax(as.numeric(end[idx]))[-length(idx)])) fail("Overlapping actor segments; double-count risk")
  }
  rows <- lapply(seq_len(nrow(b)), function(i) {
    batch <- b[i, , drop = FALSE]; ix <- which(w$batch_id == batch$batch_id)
    tot <- setNames(vapply(modes, function(mode) sum(minutes[ix][w$mode[ix] == mode], na.rm = TRUE), numeric(1)), modes)
    clean <- function(mode) any(w$mode[ix] == mode) && !any(w$mode[ix] == mode & w$record_status[ix] != "observed")
    roster <- !is.na(batch$expected_task_roster_ref) && nzchar(batch$expected_task_roster_ref)
    common_ok <- batch$common_time_capture_complete == "true" && clean("common") && roster
    normal_ok <- common_ok && batch$normal_time_capture_complete == "true" && clean("normal")
    shadow_ok <- common_ok && batch$shadow_time_capture_complete == "true" && clean("shadow")
    normal <- if (normal_ok) unname(tot["normal"] + tot["common"]) else NA_real_
    shadow <- if (shadow_ok) unname(tot["shadow"] + tot["common"]) else NA_real_
    exposure_ok <- !is.na(batch$prior_exposure_normal) && !is.na(batch$prior_exposure_shadow) &&
      batch$prior_exposure_normal == batch$prior_exposure_shadow && batch$prior_exposure_normal %in% c("none", "declared_equivalent")
    pair_ok <- normal_ok && shadow_ok && exposure_ok && batch$normal_output_status == "complete" &&
      batch$shadow_output_status == "complete" && batch$contamination == "false" &&
      all(unlist(batch[c("source_equivalent", "task_equivalent", "language_equivalent", "review_equivalent")]) == "true")
    data.frame(batch_id = batch$batch_id, case_id = batch$case_id, phase = batch$phase,
      enrolled_segments = length(ix), observed_segments = sum(w$record_status[ix] == "observed"),
      estimated_segments = sum(w$record_status[ix] == "estimated"), missing_segments = sum(missing[ix]),
      normal_recorded_minutes = unname(tot["normal"]), shadow_recorded_minutes = unname(tot["shadow"]),
      common_recorded_minutes = unname(tot["common"]), setup_recorded_minutes = unname(tot["setup"]),
      evaluation_recorded_minutes = unname(tot["evaluation"]), actual_trial_recorded_minutes = sum(tot),
      trial_capture_status = if (any(w$record_status[ix] != "observed") || !normal_ok || !shadow_ok || !all(vapply(modes, clean, logical(1)))) "incomplete_or_estimated" else "declared_complete_roster_requires_owner_verification",
      normal_process_minutes = normal, shadow_process_minutes = shadow, matched_pair_eligible = pair_ok,
      descriptive_difference_minutes = if (pair_ok) normal - shadow else NA_real_,
      interpretation = "descriptive_process_contrast_not_observed_avoided_work",
      staff_time_saved = "not_estimated", incremental_cash_savings = "not_estimated", stringsAsFactors = FALSE)
  })
  ans <- do.call(rbind, rows)
  write.csv(ans, file.path(output_dir, "workload_summary.csv"), row.names = FALSE, na = "")
  writeLines(c("DESCRIPTIVE ONLY. Authorizations and completeness declarations are not verified by this script.",
               "No causal inference, staff-saving claim, monetization or public disclosure is authorized.",
               "Recorded trial minutes omit unknown time and may include estimates; see coverage columns."),
             file.path(output_dir, "STATUS.txt"))
  invisible(ans)
}

if (sys.nframe() == 0L) {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) != 3L) stop("Usage: Rscript summarize_v10_workload.R workload.csv batches.csv output_dir", call. = FALSE)
  summarize_v10_workload(args[[1L]], args[[2L]], args[[3L]])
}
