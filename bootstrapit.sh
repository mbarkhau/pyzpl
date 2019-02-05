#!/bin/bash
# Bootstrapit Project Configuration

# Author info is used to populate
#  - License Info
#  - setup.py fields
#  - README.md contributor info
# This can also be a company or organization name and email
AUTHOR_NAME="Manuel Barkhau"
AUTHOR_EMAIL="mbarkhau@gmail.com"

KEYWORDS="zpl zmq serialization"
DESCRIPTION="ZeroMQ Property Language Parser/Serializer"

LICENSE_ID="MIT"

PACKAGE_NAME="pyzpl"
# MODULE_NAME="${PACKAGE_NAME}"
GIT_REPO_NAMESPACE="mbarkhau"
GIT_REPO_DOMAIN="gitlab.com"

PACKAGE_VERSION="v201902.0002-beta"

# These must be valid (space separated) conda package names.
# A separate conda environment will be created for each of these.
#
# Some valid options (as of late 2018) are:
# - python=2.7
# - python=3.5
# - python=3.6
# - python=3.7
# - pypy2.7
# - pypy3.5

DEFAULT_PYTHON_VERSION="python=3.7"
SUPPORTED_PYTHON_VERSIONS="python=2.7 python=3.4 python=3.7 pypy3.5"


# 1: Disables a failsafe for publishing to pypi
IS_PUBLIC=1


# PAGES_URL="https://${NAMESPACE}.${PAGES_DOMAIN}/${PACKAGE_NAME}/"

## Download and run the actual update script

if [[ $KEYWORDS == "keywords used on pypi" ]]; then
    echo "FAILSAFE! Default bootstrapit config detected.";
    echo "Did you forget to update parameters in your 'bootstrapit.sh' ?"
    exit 1;
fi

PROJECT_DIR=$(dirname "$0");

if ! [[ -f "$PROJECT_DIR/scripts/bootstrapit_update.sh" ]]; then
    mkdir -p "$PROJECT_DIR/scripts/";
    RAW_FILES_URL="https://gitlab.com/mbarkhau/bootstrapit/raw/master";
    curl --silent "$RAW_FILES_URL/scripts/bootstrapit_update.sh" \
        > "$PROJECT_DIR/scripts/bootstrapit_update.sh.tmp";
    mv "$PROJECT_DIR/scripts/bootstrapit_update.sh.tmp" \
        "$PROJECT_DIR/scripts/bootstrapit_update.sh";
fi

source "$PROJECT_DIR/scripts/bootstrapit_update.sh";
