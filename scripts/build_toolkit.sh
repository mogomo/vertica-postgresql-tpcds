#!/usr/bin/env bash
# Step "build": download and build the TPC-DS toolkit (dsdgen + dsqgen).
#
# Needs gcc, make, git and curl. The toolkit also needs flex and bison; when
# they are not installed (and there is no sudo to install them) they are built
# from source into $WORK_DIR/local, which takes about a minute.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

need gcc make git curl
mkdir -p "$WORK_DIR"

build_gnu_tool() {   # name version url
    local name=$1 ver=$2 url=$3 src="$WORK_DIR/src"
    command -v "$name" >/dev/null 2>&1 && return 0
    log "building $name $ver into $TOOLS_PREFIX"
    mkdir -p "$src"
    (
        cd "$src"
        [[ -f "$name-$ver.tar.gz" ]] || curl -sSLf -o "$name-$ver.tar.gz" "$url"
        rm -rf "$name-$ver" && tar xzf "$name-$ver.tar.gz" && cd "$name-$ver"
        # -std=gnu17: these releases do not compile under the C23 default of GCC 15
        CFLAGS="-O2 -std=gnu17" ./configure -q --prefix="$TOOLS_PREFIX" >build.log 2>&1
        make -j"$(nproc)" >>build.log 2>&1
        make install >>build.log 2>&1
    ) || die "building $name failed, see $src/$name-$ver/build.log"
}

if ! command -v flex >/dev/null || ! command -v bison >/dev/null; then
    log "flex/bison not found (sudo apt-get install -y flex bison avoids this build)"
    build_gnu_tool m4    1.4.19 https://ftp.gnu.org/gnu/m4/m4-1.4.19.tar.gz
    build_gnu_tool bison 3.8.2  https://ftp.gnu.org/gnu/bison/bison-3.8.2.tar.gz
    build_gnu_tool flex  2.6.4  https://github.com/westes/flex/releases/download/v2.6.4/flex-2.6.4.tar.gz
fi

if [[ ! -d "$KIT_DIR/.git" ]]; then
    log "cloning $KIT_REPO"
    git clone -q "$KIT_REPO" "$KIT_DIR"
fi
git -C "$KIT_DIR" -c advice.detachedHead=false checkout -q "$KIT_COMMIT"

if [[ ! -x "$KIT_DIR/tools/dsdgen" || ! -x "$KIT_DIR/tools/dsqgen" ]]; then
    log "compiling dsdgen and dsqgen"
    # The kit is old C code: relax the checks that modern GCC turns into errors.
    make -C "$KIT_DIR/tools" OS=LINUX CC=gcc LEX=flex YACC="bison -y" -j"$(nproc)" \
        BASE_CFLAGS="-D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE -DYYDEBUG -std=gnu89 -fcommon -O2 -w" \
        >"$WORK_DIR/toolkit_build.log" 2>&1 \
        || die "toolkit build failed, see $WORK_DIR/toolkit_build.log"
fi

# query dialects for dsqgen, one per product (sql/<product>/dialect.tpl)
for d in "$REPO_DIR"/sql/*/dialect.tpl; do
    cp "$d" "$KIT_DIR/query_templates/$(basename "$(dirname "$d")").tpl"
done

log "toolkit ready: $KIT_DIR/tools/dsdgen, $KIT_DIR/tools/dsqgen"
