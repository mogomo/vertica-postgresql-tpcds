#!/usr/bin/env bash
# Install PostgreSQL $PG_VERSION from the PostgreSQL community apt repository (PGDG,
# latest minor release) and create the benchmark cluster. Ubuntu / Debian, needs sudo.
#
#   scripts/postgresql/install.sh
#
#  - cluster "main" with its data directory in $PG_DATA_DIR, UTF-8, builtin C.UTF-8
#    locale (code point order: the same sort order as Vertica's default binary collation);
#  - sql/postgresql/$PG_CONF.conf as conf.d/tpcds.conf, the server log (jsonlog) in
#    $PG_LOG_DIR, readable by the run step;
#  - not started at boot (start.conf = manual): scripts/postgresql/server.sh starts and
#    stops it, so it never runs next to Vertica during a measurement;
#  - role $PG_USER (superuser) and database $PG_DB.
# Running it again only re-applies the settings file.
source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

need sudo
ETC=/etc/postgresql/$PG_VERSION/main

if ! dpkg -s "postgresql-$PG_VERSION" >/dev/null 2>&1; then
    log "adding the PGDG apt repository"
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -q postgresql-common ca-certificates curl >/dev/null
    sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y >/dev/null
    # no default cluster: it is created below with its data directory on the data disk
    sudo mkdir -p /etc/postgresql-common/createcluster.d
    echo "create_main_cluster = false" | sudo tee /etc/postgresql-common/createcluster.d/tpcds.conf >/dev/null
    log "installing postgresql-$PG_VERSION"
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -q "postgresql-$PG_VERSION" >/dev/null
fi

if ! pg_lsclusters -h | awk -v v="$PG_VERSION" '$1 == v && $2 == "main"' | grep -q .; then
    log "creating cluster $PG_VERSION/main in $PG_DATA_DIR"
    sudo install -d -o postgres -g postgres -m 700 "$PG_DATA_DIR"
    sudo pg_createcluster "$PG_VERSION" main -d "$PG_DATA_DIR" -- \
        --encoding=UTF8 --locale=C.UTF-8 --locale-provider=builtin --builtin-locale=C.UTF-8 >/dev/null
fi

sudo install -d -o postgres -g postgres -m 755 "$PG_LOG_DIR"
{ cat "$REPO_DIR/sql/postgresql/$PG_CONF.conf"
  echo "log_directory = '$PG_LOG_DIR'"; } | sudo tee "$ETC/conf.d/tpcds.conf" >/dev/null
echo manual | sudo tee "$ETC/start.conf" >/dev/null
sudo systemctl daemon-reload
sudo systemctl restart "postgresql@$PG_VERSION-main"

sudo -u postgres psql -X -q -tAc "select 1 from pg_roles where rolname = '$PG_USER'" | grep -q 1 \
    || sudo -u postgres createuser -s "$PG_USER"
sudo -u postgres psql -X -q -tAc "select 1 from pg_database where datname = '$PG_DB'" | grep -q 1 \
    || sudo -u postgres createdb -O "$PG_USER" "$PG_DB"
log "$(pg_value 'select version()' | cut -d, -f1) ready: data $PG_DATA_DIR, settings $ETC/conf.d/tpcds.conf"
