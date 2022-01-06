#!/bin/bash

die () {
    lightred='\033[1;31m'
    nocolor='\033[0m'
    echo -e "${lightred}${1}${nocolor}" >&2
    exit 1
}

print_info() {
  lightcyan='\033[1;36m'
  nocolor='\033[0m'
  echo -e "${lightcyan}[*] $1${nocolor}"
}

print_warn() {
  yellow='\e[93m'
  nocolor='\033[0m'
  echo -e "${yellow}[*] $1${nocolor}"
}
