#!/bin/bash
set -eux
mkdir -p collections
ansible-galaxy collection install --requirements-file requirements.yml --collections-path collections
