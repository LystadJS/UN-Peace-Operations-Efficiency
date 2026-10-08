#!/usr/bin/env Rscript
# Assumption-based feasibility model. NOT validated UN efficiency savings.
a <- commandArgs(trailingOnly = TRUE)
if (length(a) != 2L) stop("Usage: Rscript scripts/evaluate_conditional_options.R INPUT.csv OUTPUT_DIRECTORY")
if (!file.exists(a[[1]])) stop("Input not found.")
d <- read.csv(a[[1]], stringsAsFactors = FALSE, check.names = FALSE)
cols <- c("scenario_id","opportunity_id","scenario_class","eligible_recurring_cost_usd",
          "avoidable_fraction","annual_replacement_cost_usd","annual_mitigation_cost_usd",
          "one_time_transition_cost_usd","horizon_years","discount_rate",
          "eligible_cost_basis","mandate_review_status")
if (!all(cols %in% names(d))) stop("Missing columns: ", paste(setdiff(cols,names(d)),collapse=", "))
if (nrow(d)==0L || anyNA(d$scenario_id) || anyDuplicated(d$scenario_id)) stop("Scenario IDs invalid.")
if (anyNA(d$scenario_class) ||
    !all(d$scenario_class %in% c("synthetic","authorized_internal"))) stop("Invalid scenario class.")
if (anyNA(d$mandate_review_status) ||
    !all(d$mandate_review_status %in% c("pending","cleared","blocked"))) stop("Invalid mandate status.")
if (any(d$scenario_class=="synthetic" & d$eligible_cost_basis!="SYNTHETIC_ONLY") ||
    any(d$scenario_class=="authorized_internal" &
        d$eligible_cost_basis!="internal_ledger_verified_by_user")) stop("Missing provenance label.")
if (file.exists("data/public_opportunity_register.csv")) {
  ids <- read.csv("data/public_opportunity_register.csv")$opportunity_id
  if (any(!d$opportunity_id %in% ids)) stop("Unknown opportunity ID.")
}
inside <- function(path) {
  p <- normalizePath(path,winslash="/",mustWork=FALSE)
  root <- normalizePath(".",winslash="/",mustWork=TRUE)
  identical(p,root) || startsWith(p,paste0(root,"/"))
}
if (any(d$scenario_class=="authorized_internal") && (inside(a[[1]]) || inside(a[[2]])))
  stop("Restricted input and output must remain OUTSIDE this GitHub repository.")
numeric_fields <- cols[4:10]
if (!all(vapply(d[numeric_fields],is.numeric,logical(1))) ||
    any(!is.finite(as.matrix(d[numeric_fields])))) stop("No missing/invalid numeric assumptions permitted.")
if (any(d$eligible_recurring_cost_usd<=0) ||
    any(d$avoidable_fraction<0 | d$avoidable_fraction>1) ||
    any(d$annual_replacement_cost_usd<0) ||
    any(d$annual_mitigation_cost_usd<0) ||
    any(d$one_time_transition_cost_usd<0) ||
    any(d$horizon_years<1 | d$horizon_years>20 |
        d$horizon_years!=round(d$horizon_years)) ||
    any(d$discount_rate<0 | d$discount_rate>0.3)) stop("Assumptions outside permitted limits.")
factor <- vapply(seq_len(nrow(d)),function(i)
  sum((1+d$discount_rate[[i]])^(-seq_len(d$horizon_years[[i]]))),numeric(1))
eligible <- d$eligible_recurring_cost_usd
remainder <- d$annual_replacement_cost_usd+d$annual_mitigation_cost_usd
minimum_fraction <- (remainder+d$one_time_transition_cost_usd/factor)/eligible
modeled_npv <- factor*(eligible*d$avoidable_fraction-remainder)-d$one_time_transition_cost_usd
out <- data.frame(scenario_id=d$scenario_id,opportunity_id=d$opportunity_id,
   scenario_class=d$scenario_class,mandate_review_status=d$mandate_review_status,
   assumed_eligible_cost_usd=eligible,assumed_avoidable_fraction=d$avoidable_fraction,
   break_even_avoidable_fraction_assumption=round(minimum_fraction,6),
   break_even_possible_with_full_avoidance=minimum_fraction<=1,
   assumed_modeled_npv_usd=round(modeled_npv,2),
   action_status=ifelse(d$scenario_class=="synthetic","SYNTHETIC_TEST_NOT_EVIDENCE",
     ifelse(d$mandate_review_status=="cleared",
            "CONDITIONAL_MODEL_ONLY_INDEPENDENT_AUDIT_REQUIRED",
            "BLOCKED_PENDING_MANDATE_REVIEW")),
   verified_net_savings_usd="not_estimated",stringsAsFactors=FALSE)
dir.create(a[[2]],recursive=TRUE,showWarnings=FALSE)
write.csv(out,file.path(a[[2]],"conditional_scenarios.csv"),row.names=FALSE)
cat("Conditional model completed:",nrow(out),"rows. NO verified UN savings estimated.\n")
