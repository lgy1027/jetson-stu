#!/usr/bin/env bash
set -u

output_dir="$HOME/jetson-stu/diagnostics"
output_file="$output_dir/legacy-terminal-session-output.log"

mkdir -p "$output_dir"
: >"$output_file"

echo "tmux persistence test started: $(date --iso-8601=seconds)"
echo "host=$(hostname) user=$(whoami) pid=$$"

for index in $(seq 1 600); do
  printf 'tick=%03d time=%s\n' "$index" "$(date --iso-8601=seconds)" | tee -a "$output_file"
  sleep 1
done

echo "tmux persistence test completed: $(date --iso-8601=seconds)" | tee -a "$output_file"
