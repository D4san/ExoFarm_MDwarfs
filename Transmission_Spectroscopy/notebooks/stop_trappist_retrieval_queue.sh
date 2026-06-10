#!/usr/bin/env bash
set -euo pipefail

pkill -9 -f "run_trappist_retrieval.py --scenario A1 --n-transits 10 --instrument both" || true
pkill -9 -f "run_trappist_retrieval_campaign.py --resume" || true
pkill -9 -f "run_campaign_trappist_queue.sh" || true

sleep 2
ps -eo pid,ppid,stat,pcpu,pmem,etime,cmd \
  | grep -E "run_trappist|run_campaign_trappist|run_trappist_retrieval_campaign" \
  | grep -v grep || true
