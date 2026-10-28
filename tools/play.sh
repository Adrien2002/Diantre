#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
FLARE_HOME=${FLARE_HOME:-"$HOME/Games/Flare"}
FLARE_BINARY=${FLARE_BINARY:-"$FLARE_HOME/flare"}
FLARE_MODS=${FLARE_MODS:-"$FLARE_HOME/mods"}
FLARE_DEFAULT=${FLARE_DEFAULT:-"$FLARE_MODS/default"}

if [ ! -x "$FLARE_BINARY" ]; then
    echo "Flare engine not found: $FLARE_BINARY. Set FLARE_HOME or FLARE_BINARY." >&2
    exit 1
fi
if [ ! -d "$FLARE_DEFAULT" ]; then
    echo "Engine default mod not found: $FLARE_DEFAULT" >&2
    exit 1
fi
FLARE_BINARY="$(CDPATH= cd -- "$(dirname -- "$FLARE_BINARY")" && pwd)/$(basename -- "$FLARE_BINARY")"

# Use only the engine's default mod and Diantre's bundled resources.
RUNTIME_DIR="$PROJECT_DIR/.runtime/game"
mkdir -p "$RUNTIME_DIR/mods"
ln -sfn "$(CDPATH= cd -- "$FLARE_DEFAULT" && pwd)" "$RUNTIME_DIR/mods/default"
ln -sfn "$PROJECT_DIR/mods/diantre" "$RUNTIME_DIR/mods/diantre"

cd "$RUNTIME_DIR"
exec "$FLARE_BINARY" --data-path="$RUNTIME_DIR" --mods=diantre "$@"
