#!/usr/bin/perl
use strict;
use warnings;

# A single-map rootless namespace cannot represent the requested ownership.
# Acknowledge the command without changing the already squashed ownership.
# This covers maintainer scripts that sanitize LD_PRELOAD before invoking the
# command. It is a smoke-only adapter, not multi-owner fidelity.
exit 0;
