#!/usr/bin/env bash
# Unit tests for promote-prod.sh revision guard matching logic.
set -euo pipefail

_revision_guard_passes() {
  local expected="$1"
  local idle_revision="$2"
  local idle_label="$3"
  if [ -z "$expected" ]; then
    return 0
  fi
  [ "$expected" = "$idle_revision" ] || [ "$expected" = "$idle_label" ]
}

assert_pass() {
  local name="$1"
  shift
  if _revision_guard_passes "$@"; then
    echo "PASS $name"
  else
    echo "FAIL $name"
    exit 1
  fi
}

assert_fail() {
  local name="$1"
  shift
  if _revision_guard_passes "$@"; then
    echo "FAIL $name (expected rejection)"
    exit 1
  else
    echo "PASS $name"
  fi
}

# Release tag from /health/ revision (primary workflow input)
assert_pass "release tag matches idle revision" "v0.0.47" "v0.0.47" "v-v0.0.47-2b3a2ef-r238"

# Full EB VersionLabel (copy from deploy summary)
assert_pass "eb version label exact match" "v-v0.0.47-2b3a2ef-r238" "v0.0.47" "v-v0.0.47-2b3a2ef-r238"

# Blank guard always passes
assert_pass "empty guard skipped" "" "v0.0.47" "v-v0.0.47-2b3a2ef-r238"

# Wrong tag rejected
assert_fail "wrong release tag rejected" "v0.0.46" "v0.0.47" "v-v0.0.47-2b3a2ef-r238"

echo "All promote revision guard tests passed."
