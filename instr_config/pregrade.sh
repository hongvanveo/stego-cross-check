#!/bin/bash
homedir=$1
destdir=$2

workdir="$homedir/$destdir/stego"
resultdir="$homedir/$destdir/.local/result"
result="$resultdir/cross_check_status.txt"

mkdir -p "$resultdir"
: > "$result"

pass() { echo "PASS_$1" >> "$result"; }
fail() { echo "FAIL_$1: $2" >> "$result"; }

if [ -s "$workdir/cover.wav" ]; then
    pass "COVER_AVAILABLE"
else
    fail "COVER_AVAILABLE" "cover.wav missing"
fi

if [ -s "$workdir/marked_cross.wav" ]; then
    pass "MARKED_CREATED"
else
    fail "MARKED_CREATED" "marked_cross.wav missing"
fi

if [ -s "$workdir/.valid_checked_done" ]; then
    pass "VALID_CHECKED"
else
    fail "VALID_CHECKED" "valid verification not completed"
fi

if [ -s "$workdir/.modified_checked_done" ]; then
    pass "MODIFIED_CHECKED"
else
    fail "MODIFIED_CHECKED" "light modification verification not completed"
fi

if [ -s "$workdir/.invalid_checked_done" ]; then
    pass "INVALID_CHECKED"
else
    fail "INVALID_CHECKED" "destroyed verification not completed"
fi
