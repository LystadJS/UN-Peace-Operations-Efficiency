#!/usr/bin/env Rscript
# Synthetic-only acceptance tests. No operational measurement is loaded.
source("scripts/summarize_v10_workload.R")
template_dir <- "data/census_v10/templates"
columns <- function(name) names(read.csv(file.path(template_dir, name), check.names = FALSE))
make_row <- function(cols) as.data.frame(setNames(rep(list("SYNTHETIC"), length(cols)), cols), stringsAsFactors = FALSE)
b <- make_row(columns("batches.csv")); b$batch_id <- "SYNTHETIC_B1"; b$case_id <- "SP08P1"
b$phase <- "public_replay"; b$scope_hash <- paste(rep("a",64),collapse=""); b$input_snapshot_hash <- paste(rep("b",64),collapse="")
for(n in c("normal_time_capture_complete","shadow_time_capture_complete","common_time_capture_complete","source_equivalent","task_equivalent","language_equivalent","review_equivalent")) b[[n]] <- "true"
b$normal_output_status <- b$shadow_output_status <- "complete"
b$prior_exposure_normal <- b$prior_exposure_shadow <- "none"; b$contamination <- "false"
b$expected_task_roster_ref <- "SYNTHETIC_roster_not_institutional_approval"
modes <- c("normal","shadow","common","setup","evaluation"); mins <- c(40,30,20,10,5)
w <- do.call(rbind, lapply(seq_along(modes),function(i){
 z <- make_row(columns("workload.csv"));z$segment_id <- paste0("SYNTHETIC_S",i);z$batch_id <- b$batch_id
 z$actor_code <- paste0("SYNTHETIC_A",i); z$office_code <- "SYNTHETIC_OFFICE";z$mode<-modes[i];z$stage<-"preparation"
 z$start_utc<-"2000-01-01T00:00:00Z";z$end_utc<-format(as.POSIXct(z$start_utc,format="%Y-%m-%dT%H:%M:%SZ",tz="UTC")+60*mins[i],"%Y-%m-%dT%H:%M:%SZ",tz="UTC")
 z$active_minutes<-as.character(mins[i]);z$record_status<-"observed";z$minute_basis<-"timer";z$incident_id<-"";z$note_code<-"SYNTHETIC_ONLY";z
}))
run <- function(ww=w,bb=b){
 d<-tempfile("v10-synthetic-");dir.create(d);on.exit(unlink(d,recursive=TRUE))
 write.csv(ww,file.path(d,"w.csv"),row.names=FALSE,na="");write.csv(bb,file.path(d,"b.csv"),row.names=FALSE,na="")
 summarize_v10_workload(file.path(d,"w.csv"),file.path(d,"b.csv"),file.path(d,"out"))
}
checks <- 0L
ok <- function(value){stopifnot(isTRUE(value));checks<<-checks+1L}
reject <- function(expr){e<-tryCatch({force(expr);NULL},error=function(e)e);ok(inherits(e,"error"))}
x<-run();ok(x$actual_trial_recorded_minutes==105);ok(x$normal_process_minutes==60);ok(x$shadow_process_minutes==50)
ok(x$descriptive_difference_minutes==10);ok(x$staff_time_saved=="not_estimated" && x$incremental_cash_savings=="not_estimated")
# No records means NOT RUN, not a zero measured effect.
ok(nrow(run(w[FALSE,],b[FALSE,]))==0)
# Shared work appears once in actual trial, not once for each output.
ok(x$actual_trial_recorded_minutes==sum(mins))
# Missing/estimated time and unfinished outputs do not produce a favorable contrast.
z<-w;z$record_status[1]<-"missing";z$active_minutes[1]<-NA;z$start_utc[1]<-z$end_utc[1]<-NA
x<-run(z);ok(is.na(x$normal_process_minutes) && is.na(x$descriptive_difference_minutes) && x$missing_segments==1)
z<-w;z$record_status[1]<-"estimated";z$minute_basis[1]<-"estimate";ok(is.na(run(z)$descriptive_difference_minutes))
q<-b;q$shadow_output_status<-"failed";ok(!run(w,q)$matched_pair_eligible)
q<-b;q$source_equivalent<-"false";ok(is.na(run(w,q)$descriptive_difference_minutes))
q<-b;q$contamination<-"true";ok(!run(w,q)$matched_pair_eligible)
q<-b;q$prior_exposure_shadow<-"unequal";ok(!run(w,q)$matched_pair_eligible)
q<-b;q$normal_time_capture_complete<-"unknown";ok(is.na(run(w,q)$normal_process_minutes))
ok(is.na(run(w[w$mode!="common",])$descriptive_difference_minutes))
# Multiple distinct people contribute person-minutes; one person cannot be counted twice concurrently.
z<-w[rep(3,4),];z$mode<-"normal";z$segment_id<-paste0("SYNTHETIC_M",1:4);z$actor_code<-paste0("SYNTHETIC_PERSON",1:4)
ok(run(z)$normal_recorded_minutes==80)
reject(run(rbind(w,w[1,])))
z<-w;z$actor_code[2]<-z$actor_code[1];reject(run(z))
z<-w;z$active_minutes[1]<-"-1";reject(run(z))
z<-w;z$active_minutes[1]<-"999";reject(run(z))
z<-w;z$start_utc[1]<-"2000-01-01 00:00:00";reject(run(z))
z<-w;z$record_status[1]<-"missing";z$active_minutes[1]<-"0";reject(run(z))
q<-b;q$scope_hash<-"not_a_hash";reject(run(w,q))
q<-b;q$phase<-"substitution";reject(run(w,q))
cat(sprintf("PASS: %d synthetic workload-accounting assertions; zero live measurements.\n",checks))
