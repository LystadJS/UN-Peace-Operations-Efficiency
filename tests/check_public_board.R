#!/usr/bin/env Rscript
a <- commandArgs(trailingOnly=TRUE)
if (length(a)!=1L) stop("Provide output directory.")
d <- read.csv(file.path(a[[1]],"public_review_queue.csv"),stringsAsFactors=FALSE)
txt <- readLines(file.path(a[[1]],"public_decision_board.md"),warn=FALSE)
stopifnot(nrow(d)==18L,anyDuplicated(d$opportunity_id)==0L,
          sum(d$public_track=="now")==14L,sum(d$public_track=="watch")==3L,
          sum(d$public_track=="negative")==1L,
          all(d$incremental_net_savings_usd=="not_estimated"),
          any(grepl("cost allocation, not savings",txt,fixed=TRUE)))
cat("Public board acceptance test passed: 18 documented options, 0 validated new savings.\n")
