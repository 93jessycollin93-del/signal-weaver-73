#!/usr/bin/env bash
# Run every check for the Godot prototype. Usage: tools/scripts/test_game.sh [path/to/godot]
# Fails on any test failure or any script error printed by Godot.
set -u
GODOT="${1:-godot}"
cd "$(dirname "$0")/../../game"
status=0
"$GODOT" --headless --path . --import > /dev/null 2>&1
for script in res://tests/run_tests.gd res://tests/smoke_test.gd; do
  out=$("$GODOT" --headless --path . --script "$script" 2>&1) || status=1
  echo "== $script"; echo "$out" | grep -E "checks|FAIL|ERROR"
  echo "$out" | grep -q "SCRIPT ERROR" && status=1
done
out=$("$GODOT" --headless --path . --quit-after 300 2>&1) || status=1
echo "== main scene, 300 frames"; echo "$out" | grep -E "ERROR" || echo "no errors"
echo "$out" | grep -q "ERROR" && status=1
exit $status
