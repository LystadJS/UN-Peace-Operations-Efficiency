#!/usr/bin/env Rscript
# Deliberately synthetic fixture. No live staff logs or approval records.
source('scripts/summarize_v10_workload.R')
cols <- function(file) names(read.csv(file.path('data/census_v10/templates',file),check.names=FALSE))
row <- function(names) as.data.frame(setNames(rep(list('SYNTHETIC'),length(names)),names),stringsAsFactors=FALSE)
b <- row(cols('batches.csv')); b$batch_id <- 'SYNTHETIC_SC11'; b$case_id <- 'SP08P1'; b$phase <- 'public_replay'
b$scope_hash <- strrep('a',64);b$input_snapshot_hash <- strrep('b',64)
for(k in c('normal_time_capture_complete','shadow_time_capture_complete','common_time_capture_complete','source_equivalent','task_equivalent','language_equivalent','review_equivalent')) b[[k]] <- 'true'
b$normal_output_status <- b$shadow_output_status <- 'complete';b$prior_exposure_normal <- b$prior_exposure_shadow <- 'none';b$contamination <- 'false'
b$expected_task_roster_ref <- 'SYNTHETIC_no_owner_authority'
modes <- c(rep('common',4),'normal','shadow','setup','evaluation');mins <- c(rep(20,4),10,8,5,7)
w <- do.call(rbind,lapply(seq_along(mins),function(i){z<-row(cols('workload.csv'));z$segment_id<-paste0('SYNTHETIC_',i);z$batch_id<-b$batch_id;z$actor_code<-paste0('SYNTHETIC_ACTOR_',i);z$office_code<-'SYNTHETIC';z$mode<-modes[i];z$stage<-'SYNTHETIC';z$start_utc<-'2000-01-01T00:00:00Z';z$end_utc<-format(as.POSIXct(z$start_utc,format='%Y-%m-%dT%H:%M:%SZ',tz='UTC')+60*mins[i],'%Y-%m-%dT%H:%M:%SZ',tz='UTC');z$active_minutes<-as.character(mins[i]);z$record_status<-'observed';z$minute_basis<-'synthetic_timer';z}))
run <- function(ww){d<-tempfile();dir.create(d);on.exit(unlink(d,recursive=TRUE));write.csv(ww,file.path(d,'w.csv'),row.names=FALSE,na='');write.csv(b,file.path(d,'b.csv'),row.names=FALSE,na='');summarize_v10_workload(file.path(d,'w.csv'),file.path(d,'b.csv'),file.path(d,'out'))}
x<-run(w);stopifnot(x$common_recorded_minutes==80,x$actual_trial_recorded_minutes==110,x$normal_process_minutes==90,x$shadow_process_minutes==88,x$descriptive_difference_minutes==2,x$staff_time_saved=='not_estimated',x$incremental_cash_savings=='not_estimated')
w$record_status[5]<-'missing';w$active_minutes[5]<-NA;w$start_utc[5]<-w$end_utc[5]<-NA
x<-run(w);stopifnot(is.na(x$normal_process_minutes),is.na(x$descriptive_difference_minutes),x$missing_segments==1)
cat('PASS: 10 synthetic SC11 assertions; no live records or staff-saving estimate.\n')
