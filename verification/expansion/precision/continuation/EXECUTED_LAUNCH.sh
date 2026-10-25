#!/usr/bin/env bash
# Prepared launcher. Execute only after the coordinator assigns a browser slot.
set -u
cd /workspace/fallout-Marseille || exit 1
continuation_qa_output=/workspace/.cloud-setup/fallout-marseille/precision-expansion/continuation-native
mkdir -p "$continuation_qa_output"
cp "$0" "$continuation_qa_output/EXECUTED_LAUNCH.sh"
python tests/expansion/continuation_native.py \
  --run \
  --output "$continuation_qa_output" \
  --expect-html-sha 120e04972fb08a6f59b929d8a0952010712cf3849b8e512c383ff3a8ae87d636 \
  --expect-architecture-sha c5c853a51c56d5b9f9f5dd75085de8ef524d6a0c3efd774fbbbe099daf82f229 \
  --expect-lore-sha 85264d16726c054bacb9763fd87b1e5b011f37bd76f6662bfceebc2b34dccfe3 \
  --expect-power-sha 77e03d9b83f7d35828de22dc13abd6e368879eaeeb5537f39576824a41386ebc \
  --expect-iconic-sha 550ee004344e4879c0d87164ab97971978113c882e0ca5a2a2045a61b5725e23 \
  > "$continuation_qa_output/execution.log" 2>&1
continuation_qa_status=$?
printf '%s\n' "$continuation_qa_status" > "$continuation_qa_output/exit-code.txt"
exit "$continuation_qa_status"
