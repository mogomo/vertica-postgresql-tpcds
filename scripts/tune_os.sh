#!/usr/bin/env bash
# Check / apply the Linux settings Vertica recommends for best performance.
#
#   scripts/tune_os.sh            show current vs recommended values (no root needed)
#   sudo scripts/tune_os.sh apply     apply now (lost on reboot)
#   sudo scripts/tune_os.sh persist   apply now and keep after reboot
#   sudo scripts/tune_os.sh revert    remove the persistent files written by "persist"
#
# Covers the items that Vertica's own check reports on a stock Ubuntu install
# (python3 -m vertica.local_verify): CPU frequency governor, disk readahead,
# vm.max_map_count and vm.swappiness, plus the power profile and the lid switch
# (closing the lid must not suspend the machine during a run) on laptops.
set -euo pipefail

MODE=${1:-check}
DATA_PATH=${DATA_PATH:-/home/dbadmin}   # any path on the Vertica data disk
READAHEAD_SECTORS=2048                  # Vertica minimum (1 MiB)
SWAPPINESS=1

SYSCTL_FILE=/etc/sysctl.d/99-vertica-tuning.conf
UDEV_FILE=/etc/udev/rules.d/60-vertica-readahead.rules
UNIT_FILE=/etc/systemd/system/vertica-cpu-performance.service
LID_FILE=/etc/systemd/logind.conf.d/90-vertica-lid.conf
SLEEP_TARGETS="suspend.target hibernate.target hybrid-sleep.target suspend-then-hibernate.target"

mem_kb=$(awk '/MemTotal/ { print $2 }' /proc/meminfo)
MIN_MAP_COUNT=$(( mem_kb / 16 > 65530 ? mem_kb / 16 : 65530 ))   # Vertica rule: RAM in KB / 16
# value written: rounded up to a multiple of 65536, as MemTotal varies slightly between boots
MAX_MAP_COUNT=$(( (MIN_MAP_COUNT + 65535) / 65536 * 65536 ))

# whole disk (e.g. nvme0n1) that holds DATA_PATH
src=$(findmnt -no SOURCE -T "$DATA_PATH")
DISK=$(lsblk -no PKNAME "$src" 2>/dev/null | head -1)
DISK=${DISK:-$(basename "$src")}

rd() { cat "$1" 2>/dev/null || echo n/a; }
governors() { cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null | sort | uniq -c | awk '{ printf "%s%s x%s", sep, $2, $1; sep=", " }'; }
row() { printf '  %-28s %-26s %-14s %s\n' "$1" "$2" "$3" "$4"; }
status() { [[ "$1" == "$2" ]] && echo ok || echo CHANGE; }
has_lid() { compgen -G '/proc/acpi/button/lid/*' >/dev/null; }
lid_action() { busctl get-property org.freedesktop.login1 /org/freedesktop/login1 \
    org.freedesktop.login1.Manager "$1" 2>/dev/null | awk '{ gsub(/"/, "", $2); print $2 }'; }

check() {
    local ra gov thp prof
    ra=$(blockdev --getra "/dev/$DISK" 2>/dev/null || awk '{ print $1 * 2 }' "/sys/block/$DISK/queue/read_ahead_kb")
    gov=$(governors)
    thp=$(sed -E 's/.*\[(.*)\].*/\1/' /sys/kernel/mm/transparent_hugepage/enabled)
    prof=$(command -v powerprofilesctl >/dev/null && powerprofilesctl get 2>/dev/null || rd /sys/firmware/acpi/platform_profile)
    row SETTING CURRENT RECOMMENDED STATUS
    row "cpu governor" "$gov" performance "$([[ "$gov" == performance* && "$gov" != *,* ]] && echo ok || echo CHANGE)"
    row "power profile" "$prof" performance "$(status "$prof" performance)"
    row "readahead /dev/$DISK" "$ra sectors" "$READAHEAD_SECTORS" "$( (( ra >= READAHEAD_SECTORS )) && echo ok || echo CHANGE)"
    row vm.max_map_count "$(sysctl -n vm.max_map_count)" ">= $MIN_MAP_COUNT" "$( (( $(sysctl -n vm.max_map_count) >= MIN_MAP_COUNT )) && echo ok || echo CHANGE)"
    row vm.swappiness "$(sysctl -n vm.swappiness)" "$SWAPPINESS" "$(status "$(sysctl -n vm.swappiness)" "$SWAPPINESS")"
    row "transparent hugepages" "$thp" "madvise/always" "$([[ $thp != never ]] && echo ok || echo CHANGE)"
    row "turbo boost" "$([[ $(rd /sys/devices/system/cpu/intel_pstate/no_turbo) == 1 ]] && echo off || echo on)" on ""
    row "on AC power" "$(for f in /sys/class/power_supply/*/type; do if [[ $(rd "$f") == Mains ]]; then rd "${f%/type}/online"; fi; done | head -1)" 1 ""
    if has_lid; then
        local lid="$(lid_action HandleLidSwitch)/$(lid_action HandleLidSwitchExternalPower)"
        row "lid close (battery/AC)" "$lid" ignore/ignore "$(status "$lid" ignore/ignore)"
    fi
}

apply() {
    [[ $EUID -eq 0 ]] || { echo "run with sudo" >&2; exit 1; }
    for g in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo performance > "$g"; done
    if command -v powerprofilesctl >/dev/null; then powerprofilesctl set performance || true; fi
    blockdev --setra "$READAHEAD_SECTORS" "/dev/$DISK"
    sysctl -q -w vm.max_map_count="$MAX_MAP_COUNT" vm.swappiness="$SWAPPINESS"
}

persist() {
    apply
    printf 'vm.max_map_count = %s\nvm.swappiness = %s\n' "$MAX_MAP_COUNT" "$SWAPPINESS" > "$SYSCTL_FILE"
    printf 'ACTION=="add|change", KERNEL=="%s", ATTR{queue/read_ahead_kb}="%s"\n' \
        "$DISK" $(( READAHEAD_SECTORS / 2 )) > "$UDEV_FILE"
    # runs at boot and again after every resume (resume resets the governor)
    cat > "$UNIT_FILE" <<EOF
[Unit]
Description=CPU frequency governor = performance (Vertica)
After=power-profiles-daemon.service $SLEEP_TARGETS

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'for g in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo performance > \$g; done'

[Install]
WantedBy=multi-user.target $SLEEP_TARGETS
EOF
    if has_lid; then
        mkdir -p "$(dirname "$LID_FILE")"
        printf '[Login]\nHandleLidSwitch=ignore\nHandleLidSwitchExternalPower=ignore\nHandleLidSwitchDocked=ignore\n' > "$LID_FILE"
        systemctl kill -s HUP systemd-logind   # reload logind.conf without ending sessions
    fi
    systemctl daemon-reload
    systemctl reenable -q vertica-cpu-performance.service
    echo "written: $SYSCTL_FILE $UDEV_FILE $UNIT_FILE$(has_lid && echo " $LID_FILE")"
}

revert() {
    [[ $EUID -eq 0 ]] || { echo "run with sudo" >&2; exit 1; }
    systemctl disable -q vertica-cpu-performance.service 2>/dev/null || true
    rm -f "$SYSCTL_FILE" "$UDEV_FILE" "$UNIT_FILE" "$LID_FILE"
    systemctl daemon-reload
    systemctl kill -s HUP systemd-logind 2>/dev/null || true
    echo "removed persistent settings; they reset to the OS defaults on the next reboot"
}

case "$MODE" in
    check)   check ;;
    apply)   apply;   check ;;
    persist) persist; check ;;
    revert)  revert ;;
    *) sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
