#!/usr/bin/env sh
set -eu

# Accept only the exact command in the pinned public base Dockerfile. Create
# the same named account without requesting an unrepresentable home owner.
if [ "$#" -ne 4 ] || \
   [ "$1" != "--disabled-password" ] || \
   [ "$2" != "--gecos" ] || \
   [ "$3" != "dog" ] || \
   [ "$4" != "nonroot" ]; then
  printf '%s\n' 'singlemap_adduser_v1: unexpected arguments; refusing' >&2
  exit 64
fi

/usr/sbin/useradd -M -U -u 1000 -c dog -s /bin/bash nonroot
mkdir -p /home/nonroot
chmod 0750 /home/nonroot
