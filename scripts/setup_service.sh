#!/bin/bash
# ==============================================================================
# setup_service.sh
# ==============================================================================
# Manages persistent background execution for thinking buffer via macOS launchd.
#
# Usage:
#   ./scripts/setup_service.sh install    # Register and start service on login
#   ./scripts/setup_service.sh uninstall  # Stop and unregister service
#   ./scripts/setup_service.sh status     # Check launchd service status
#   ./scripts/setup_service.sh logs       # View launchd log output
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PLIST_NAME="com.thinkingbuffer.dev.plist"
SOURCE_PLIST="${SCRIPT_DIR}/${PLIST_NAME}"
TARGET_DIR="${HOME}/Library/LaunchAgents"
TARGET_PLIST="${TARGET_DIR}/${PLIST_NAME}"

ACTION="${1:-status}"

case "$ACTION" in
    install)
        mkdir -p "${TARGET_DIR}"
        cp "${SOURCE_PLIST}" "${TARGET_PLIST}"
        launchctl unload "${TARGET_PLIST}" 2>/dev/null || true
        launchctl load "${TARGET_PLIST}"
        echo "Installed and loaded ${PLIST_NAME} into ${TARGET_DIR}."
        echo "Thinking Buffer is now running at http://localhost:4321 and will start on login."
        ;;
    uninstall)
        if [ -f "${TARGET_PLIST}" ]; then
            launchctl unload "${TARGET_PLIST}" 2>/dev/null || true
            rm -f "${TARGET_PLIST}"
            echo "Unloaded and removed ${TARGET_PLIST}."
        else
            echo "Service is not installed."
        fi
        ;;
    status)
        if launchctl list | grep -q "com.thinkingbuffer.dev"; then
            echo "Service 'com.thinkingbuffer.dev' is ACTIVE."
            launchctl list | grep "com.thinkingbuffer.dev"
        else
            echo "Service 'com.thinkingbuffer.dev' is NOT loaded in launchd."
        fi
        ;;
    logs)
        tail -f "${REPO_DIR}/.astro/launchd.log"
        ;;
    *)
        echo "Usage: $0 {install|uninstall|status|logs}"
        exit 1
        ;;
esac
