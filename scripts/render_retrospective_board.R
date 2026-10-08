#!/usr/bin/env Rscript
# Public-only retrospective evidence board. Input contains no restricted records.
# Source-count coverage and sample examples are NOT estimates of UN duplication.
args <- commandArgs(trailingOnly=TRUE)
if(length(args)!=2L) {
  stop("Usage: Rscript scripts/render_retrospective_board.R REPOSITORY_ROOT OUTPUT_DIR",
       call.=FALSE)
}
root <- args[[1L]]
dest <- args[[2L]]
read_data <- function(name) {
  path <- file.path(root,"data",paste0(name,".csv"))
  if(!file.exists(path)) stop("Missing required data: ",path)
  read.csv(path,stringsAsFactors=FALSE,check.names=FALSE)
}
s <- read_data("retrospective_2025_2026_sources")
a <- read_data("retrospective_2025_2026_activities")
m <- read_data("retrospective_2025_2026_matches")
p <- read_data("public_deliverable_crosswalk_2027")
g <- read_data("retrospective_2025_2026_summary")
d <- read_data("retrospective_2025_2026_reuse_decisions")
stopifnot(nrow(s)==42L,nrow(a)==38L,nrow(m)==36L,nrow(p)==32L,
          nrow(g)==4L,nrow(d)==11L)
stopifnot(sum(a$analysis_period_status=="2024_excluded")==1L)
stopifnot(sum(p$retrospective_sample_coverage=="matched_in_purposive_sample")==19L)
stopifnot(all(m$separately_paid_duplicate_work_found=="no"))
stopifnot(all(m$incremental_net_savings_usd=="not_estimated"))
stopifnot(all(d$incremental_cost_avoided_usd=="not_estimated"))
if(anyDuplicated(a$activity_id)||anyDuplicated(m$match_id)||
   anyDuplicated(p$output_pair_id)||anyDuplicated(d$case_id)) {
  stop("Missing canonical identity uniqueness")
}
order <- match(d$research_rank, seq_len(nrow(d)))
if(anyNA(order)||anyDuplicated(order)) stop("Incorrect reuse rank order")
d <- d[order(d$research_rank),,drop=FALSE]
board <- d[,c("research_rank","case_id","entities","common_function",
              "reuse_evidence_type","what_is_verified","feasible_public_workflow_change",
              "legal_temporal_scope_guardrail","incremental_cost_avoided_usd")]
dir.create(dest,recursive=TRUE,showWarnings=FALSE)
if(!dir.exists(dest)) stop("Failed creating output")
write.csv(board,file.path(dest,"reusable_work_review_queue.csv"),row.names=FALSE)
write.csv(g,file.path(dest,"four_group_retrospective_summary.csv"),row.names=FALSE)
escape <- function(x) gsub("|","/",x,fixed=TRUE)
lines <- c(
 "# Actual 2025–2026 work reuse: selected public UN evidence",
 "",
 "**Scope:** 42 official-source records; 38 canonical activities/products, of which one is a 2024 workshop excluded from 2025–2026 counts.",
 "**Matches:** 36 adjudicated relationships; 19 of 32 planned 2027 output categories have retrospective examples.",
 "**Financial result:** No separately charged duplicate service verified; incremental net savings **not estimated**.",
 "",
 "## Four comparison groups",
 "",
 "| Pairing | Adjudications | Planned 2027 categories matched in this selected sample | Duplicated paid cost identified |",
 "|---|---:|---:|---|"
)
for(i in seq_len(nrow(g))) {
  x <- g[i,,drop=FALSE]
  lines <- c(lines,paste0("| ",x$pairing," | ",x$retrospective_adjudication_records,
                            " | ",x$categories_with_retrospective_support,"/8 | No |"))
}
lines <- c(lines,"","## Reuse review queue","",
           "| Priority | Case | Verified source relation | Possible reusable process |",
           "|---:|---|---|---|")
for(i in seq_len(nrow(d))) {
  x <- d[i,,drop=FALSE]
  lines <- c(lines,paste0("| ",x$research_rank," | ",x$case_id," | ",
                          escape(x$what_is_verified)," | ",
                          escape(x$feasible_public_workflow_change)," |"))
}
lines <- c(lines,"",
 "**Do not:** Interpret common topics or dates as duplicate mandates; infer cost savings without matched charges, service continuation and legal authorization; count October 2024 training as a 2025 activity.",
 "",
 "Evidence: data/retrospective_2025_2026_{sources,activities,matches,reuse_decisions}.csv.",
 "")
writeLines(lines,file.path(dest,"retrospective_review_board.md"),useBytes=TRUE)
cat("RETROSPECTIVE BOARD GENERATED: 42 sources, 38 activities (1 excluded), 36 matches, 19/32 2027 categories represented.\n")
cat("Verified duplicate financed service: NONE IDENTIFIED. Incremental net savings: NOT ESTIMATED.\n")
