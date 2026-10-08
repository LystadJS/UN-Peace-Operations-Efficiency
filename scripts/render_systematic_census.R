#!/usr/bin/env Rscript
# Public-only Council-report, meeting, activity and training census view.
# Index coverage is not content duplication and cannot quantify cost savings.
args <- commandArgs(trailingOnly=TRUE)
if(length(args)!=2L) stop("Usage: Rscript scripts/render_systematic_census.R REPO_ROOT OUTPUT_DIRECTORY")
root <- args[[1L]]
out <- args[[2L]]
read_data <- function(name) {
  file <- file.path(root,"data",paste0(name,".csv"))
  if(!file.exists(file)) stop("Missing indexed evidence: ",file)
  read.csv(file,stringsAsFactors=FALSE,check.names=FALSE)
}
r <- read_data("systematic_sg_reports_2025_2026")
m <- read_data("systematic_sc_meetings_2025_2026")
a <- read_data("retrospective_2025_2026_activities")
master <- read_data("systematic_master_record_views_2025_2026")
q <- read_data("systematic_shared_production_options")
extra <- read_data("systematic_2025_2026_additional_matches")
bench <- read_data("systematic_council_meeting_population_benchmark")
if(nrow(r)!=132L || nrow(m)!=474L || nrow(a)!=46L || nrow(master)!=652L ||
   nrow(q)!=13L || nrow(extra)!=9L) stop("Unexpected source population: rerun validation.")
if(anyDuplicated(r$document_symbol) || anyDuplicated(m$record_id) ||
   anyDuplicated(master$item_id)) stop("Duplicated source identities")
distinct <- function(v) length(unique(v))
a2025 <- r[r$index_year==2025,,drop=FALSE]
a2026 <- r[r$index_year==2026,,drop=FALSE]
m2025 <- m[m$year==2025,,drop=FALSE]
m2026 <- m[m$year==2026,,drop=FALSE]
if(distinct(m2025$meeting_base_id)!=255L ||
   distinct(m2026$meeting_base_id)!=151L) stop("Formal meeting ID denominator mismatch.")
if(sum(tolower(as.character(r$date_year_mismatch))=="true")!=1L)stop("Source data-quality anomaly count changed.")
if(sum(a$analysis_period_status=="2024_excluded")!=1L)
  stop("2024 postevent publication must stay excluded.")
if(any(q$verified_new_net_savings_usd!="not_estimated"))
  stop("Unsupported monetary savings must not appear.")
source_status <- data.frame(
  record_layer=c("Secretary-General official annual index: 2025",
                 "Secretary-General official annual index: 2026",
                 "Council meeting record variants: 2025",
                 "Distinct 2025 formal Council meetings",
                 "Council meeting record variants: 2026 through snapshot",
                 "Distinct 2026 formal Council meetings through snapshot",
                 "Canonical mission and training activities",
                 "New 2026 case adjudications"),
  count=c(nrow(a2025),nrow(a2026),nrow(m2025),
          distinct(m2025$meeting_base_id),nrow(m2026),
          distinct(m2026$meeting_base_id),nrow(a),nrow(extra)),
  completeness=c("Official listed SG reports, not entire UN product universe",
                 "Official indexed to 8 October; year incomplete",
                 "Variant records include resumptions",
                 "2025 official total validated; 115 informal consultations excluded",
                 "2026 may lag or be subsequently revised",
                 "Index snapshot, not final calendar year",
                 "Selected public mission websites, not total event universe",
                 "Source-matched supplemental cases, not financial duplication"),
  stringsAsFactors=FALSE
)
q <- q[order(q$public_priority),,drop=FALSE]
dir.create(out,recursive=TRUE,showWarnings=FALSE)
write.csv(source_status,file.path(out,"systematic_census_counts.csv"),row.names=FALSE)
write.csv(q,file.path(out,"systematic_shared_production_queue.csv"),row.names=FALSE)
lines <- c("# UN peace-operations actual-work census — public source snapshot",
  "",
  "**As of 8 October 2026.** Council index symbols are broader than the 78-report targeted research slice; field visit and training activity collection remains non-exhaustive.",
  "",
  "## Count and coverage controls","","| Source layer | Entries | Coverage |",
  "|---|---:|---|")
for(i in seq_len(nrow(source_status))) {
  x <- source_status[i,]
  lines <- c(lines,paste0("| ",x$record_layer," | ",x$count," | ",x$completeness," |"))
}
lines <- c(lines,"",
  "The official 2025 Security Council annual benchmark is **255 formal meetings** (235 public, 20 private), plus **115 informal consultations** that are not included in the formal meeting ledger.",
  "A report's title or a meeting's shared geography is not evidence of common text, effort or duplicated service.",
  "",
  "## Public-research shared-production priorities","","| Priority | Entities | Actual work or comparison | Evidence grade |",
  "|---:|---|---|---|")
clean <- function(x) gsub("|","/",x,fixed=TRUE)
for(i in seq_len(nrow(q))) {
  x <- q[i,]
  lines <- c(lines,paste0("| ",x$public_priority," | ",clean(x$entities)," | ",
    clean(x$proposed_shared_production_area)," | ",x$evidence_grade," |"))
}
lines <- c(lines,"",
 "**No incremental net savings have been estimated.** Requests for financial reductions require matched source/recipient costs, legal mandate review, service performance and transition liabilities.",
 "",
 "Source files: data/systematic_sg_reports_2025_2026.csv; data/systematic_sc_meetings_2025_2026.csv; data/retrospective_2025_2026_activities.csv; data/systematic_shared_production_options.csv.","")
writeLines(lines,file.path(out,"systematic_public_census_board.md"),useBytes=TRUE)
cat("SYSTEMATIC PUBLIC BOARD: 132 SG reports, 474 meeting record variants, 406 distinct formal meetings across 2025 and 2026 snapshot; 46 mission events; 13 source-based review ideas.\n")
