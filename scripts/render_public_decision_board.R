#!/usr/bin/env Rscript
# Generate public-only executive board from the review register.
a <- commandArgs(trailingOnly=TRUE)
if (length(a)!=2L) stop("Usage: Rscript scripts/render_public_decision_board.R ROOT OUTPUT_DIRECTORY")
read_csv <- function(name) read.csv(file.path(a[[1]],"data",paste0(name,".csv")),
                                     stringsAsFactors=FALSE,check.names=FALSE)
x <- read_csv("public_opportunity_register")
g <- read_csv("public_release_gates")
n <- read_csv("public_finance_nodes")
if (nrow(x)!=18L || nrow(g)!=18L || anyDuplicated(x$opportunity_id) ||
    !setequal(x$opportunity_id,g$opportunity_id)) stop("Bad opportunity or gate roster.")
if (any(x$incremental_net_savings_usd!="not_estimated") ||
    any(g$additional_net_savings_usd!="not_estimated")) stop("Unsupported savings claim.")
if (sum(x$public_track=="now")!=14L || sum(x$public_track=="watch")!=3L ||
    sum(x$public_track=="negative")!=1L) stop("Unexpected public-decision class.")
find_amount <- function(id) {
  z <- n$amount_usd_thousands[n$finance_id==id]
  if (length(z)!=1L) stop("Unknown finance ID.")
  as.numeric(z)
}
if (abs(find_amount("SPM27_EFF_UF")-438.1)>.001 ||
    abs(find_amount("SPM27_EFF_BINUH")-1400)>.001 ||
    abs(find_amount("SPM27_RSCE")-3259.1)>.001) stop("Finance baseline moved.")
x <- x[order(match(x$readiness_tier,c("T1","T2","T3","T4","T0")),x$opportunity_id),]
view <- x[,c("opportunity_id","readiness_tier","short_title","public_track",
            "public_work_package","mandate_risk","incremental_net_savings_usd")]
dir.create(a[[2]],recursive=TRUE,showWarnings=FALSE)
write.csv(view,file.path(a[[2]],"public_review_queue.csv"),row.names=FALSE)
safe <- function(z) gsub("|","/",z,fixed=TRUE)
lines <- c("# Public evidence decision board",
           "",
           "All monetary values here are published funding or existing estimated efficiencies, not new savings.",
           "",
           "Public actions now: 14 | Monitor existing proposals: 3 | Protected negative controls: 1.",
           "",
           "Budgeted UNIFIL asset transfer avoidance: $438,100; BINUH aviation reduction: $1,400,000.",
           "RSCE $3,259,100 is an SPM cost allocation, not savings.",
           "",
           "| ID | Tier | Area | Public-only next step | Mandate risk |",
           "|---|---|---|---|---|")
for (i in seq_len(nrow(x))) {
  z <- x[i,]
  lines <- c(lines,paste("|",z$opportunity_id,"|",z$readiness_tier,"|",
                         safe(z$short_title),"|",safe(z$public_work_package),"|",
                         z$mandate_risk,"|"))
}
lines <- c(lines,"","No program can be cut on this evidence alone: require legal authority, verified unique costs and mandate protection.")
writeLines(lines,file.path(a[[2]],"public_decision_board.md"),useBytes=TRUE)
cat("Board generated: 18 public opportunities; no additional savings estimated.\n")
