#!/bin/sh
DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if command -v xdg-open >/dev/null 2>&1; then xdg-open "$DIR/JOUER_FALLOUT_MISTRAL_v0.49.html"
elif command -v open >/dev/null 2>&1; then open "$DIR/JOUER_FALLOUT_MISTRAL_v0.49.html"
else printf '%s\n' "Ouvrez $DIR/JOUER_FALLOUT_MISTRAL_v0.49.html dans votre navigateur."
fi
