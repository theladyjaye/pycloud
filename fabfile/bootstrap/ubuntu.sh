#! /bin/bash
apt-get update -qq
apt-get install -y -q ruby libshadow-ruby1.8
apt-get install -y -q puppet facter