#!/usr/bin/env Rscript
a <- commandArgs(trailingOnly=TRUE)
if (length(a)!=1L) stop("Provide output directory.")
d <- read.csv(file.path(a[[1]],"conditional_scenarios.csv"),stringsAsFactors=FALSE)
stopifnot(nrow(d)==3L,all(d$scenario_class=="synthetic"),
          all(d$verified_net_savings_usd=="not_estimated"),
          all(d$action_status=="SYNTHETIC_TEST_NOT_EVIDENCE"))
stopifnot(abs(d$assumed_modeled_npv_usd[[1]]-320)<.01,
          abs(d$assumed_modeled_npv_usd[[2]]+200)<.01,
          abs(d$break_even_avoidable_fraction_assumption[[1]]-.093333)<.00001,
          d$assumed_modeled_npv_usd[[3]]<0)
cat("Synthetic break-even tests passed: 1 positive, 2 negative, 0 UN savings claims.\n")
