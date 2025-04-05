#!/bin/sh
set -e

posix_read() {
    prompt="${1}"
    var_name="${2}"
    printf "%s: " "${prompt}"
    read -r "${var_name?}"
    export "${var_name?}"
    return ${?}
}

posix_read "Tag" VERSION
posix_read "PyPI username" UV_PUBLISH_USERNAME
posix_read "PyPI password" UV_PUBLISH_PASSWORD
posix_read "Discord deployment webhook URL" DEPLOY_WEBHOOK_URL

bash scripts/ci/release.sh
