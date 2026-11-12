#!/bin/sh
set -eu

# Restrict the relay to the one destination the implant is supposed to reach.
# A stolen tunnel cannot be repointed at another service on the protected
# segment.
exec wstunnel server --log-lvl=INFO --restrict-to beacon:80 ws://0.0.0.0:8080
