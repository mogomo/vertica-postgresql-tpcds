#!/usr/bin/env bash
# Step "env": describe the test environment as Markdown (stdout).
#
# Only hardware/software facts are collected. Host names, IP addresses and
# user names are deliberately left out so the output can be published.
# The rows about the database come from the product (db_env_rows).
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

rd() { cat "$1" 2>/dev/null | head -1 || true; }

cpu=$(lscpu | sed -n 's/^Model name:[[:space:]]*//p' | head -1)
sockets=$(lscpu | sed -n 's/^Socket(s):[[:space:]]*//p')
cores=$(lscpu -p=core,socket | grep -v '^#' | sort -u | wc -l)
threads=$(nproc --all)
maxmhz=$(lscpu | sed -n 's/^CPU max MHz:[[:space:]]*//p' | cut -d. -f1)
l3=$(lscpu | sed -n 's/^L3 cache:[[:space:]]*//p')
mem=$(awk '/MemTotal/ { printf "%.1f GiB", $2 / 1048576 }' /proc/meminfo)
swap=$(awk '/SwapTotal/ { printf "%.1f GiB", $2 / 1048576 }' /proc/meminfo)
model="$(rd /sys/class/dmi/id/sys_vendor) $(rd /sys/class/dmi/id/product_name)"
chassis=$(rd /sys/class/dmi/id/chassis_type)
case "$chassis" in 8|9|10|14|31|32) kind=laptop ;; 3|4|6|7|13|15|35|36) kind=desktop ;; 17|23|28|29) kind=server ;; 1) kind="virtual machine" ;; *) kind="other ($chassis)" ;; esac
[[ -n "$(rd /sys/class/dmi/id/product_name)" ]] || kind=unknown
os=$(. /etc/os-release && echo "$PRETTY_NAME")
kernel=$(uname -r)
governor=$(rd /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
epp=$(rd /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference)
profile=$(rd /sys/firmware/acpi/platform_profile)
ac=$(for f in /sys/class/power_supply/*/type; do
         if [[ "$(rd "$f")" == Mains ]]; then rd "${f%/type}/online"; fi
     done | head -1)
virt=$(systemd-detect-virt 2>/dev/null || true)
[[ "$virt" != none ]] || virt=""

if [[ -n "${QUERY_BUDGETS:-}" ]]; then
    limits="time limit per query from budgets.csv (max(60 s, 5 x Vertica best time)); a query over its limit is not run again"
else
    limits="query timeout ${QUERY_TIMEOUT}s"
fi
[[ -n "${QUERIES:-}" ]] && limits+=", queries: $QUERIES"
[[ "$PRODUCT" == postgresql ]] || PG_COPY_STREAMS=

data_path=$(db_data_path || true)
disk_src=$(findmnt -no SOURCE -T "${data_path:-/}" 2>/dev/null || true)
fstype=$(findmnt -no FSTYPE -T "${data_path:-/}" 2>/dev/null || true)
disk_dev=$(lsblk -no PKNAME "$disk_src" 2>/dev/null | head -1)
disk_model=$(rd "/sys/block/$disk_dev/device/model" | sed 's/[[:space:]]*$//')
disk_size=$(lsblk -dno SIZE "/dev/$disk_dev" 2>/dev/null | tr -d ' ')
disk_rot=$(rd "/sys/block/$disk_dev/queue/rotational")
disk_kind=$([[ "$disk_dev" == nvme* ]] && echo "NVMe SSD" || { [[ "$disk_rot" == 0 ]] && echo SSD || echo HDD; })

cat <<EOF
## Environment

| | |
|---|---|
| Date | $(date -u '+%Y-%m-%d %H:%M UTC') |
| Machine | $model ($kind) |
| CPU | $cpu - $sockets socket(s), $cores cores, $threads threads, max ${maxmhz} MHz, L3 $l3 |
| Memory | $mem RAM, $swap swap |
| Storage (database data) | ${disk_size} ${disk_kind} ${disk_model:+($disk_model)}, $fstype |
| OS | $os, kernel $kernel${virt:+, virtualization: $virt} |
| Power | governor=${governor:-n/a}, energy_perf_pref=${epp:-n/a}, platform_profile=${profile:-n/a}, on AC=${ac:-n/a} |
$(db_env_rows)

## Benchmark settings

| | |
|---|---|
| Scale factor | $SCALE |
| Toolkit | tpcds-kit @ ${KIT_COMMIT:0:7}, queries generated with -QUALIFY Y (fixed spec parameters) |
| Iterations | $ITERATIONS, $limits |
| dsdgen jobs / load jobs | $JOBS / $LOAD_JOBS tables at a time${PG_COPY_STREAMS:+ (PostgreSQL: up to $PG_COPY_STREAMS files per table)} |
EOF
