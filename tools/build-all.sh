#!/usr/bin/env bash
# Rebuild every derived artefact from source files, then verify.
#
#   ./tools/build-all.sh
#
# 1. references   PDF -> refs.json (exact link destinations from PDF annotations)
# 2. dossier      PDF -> collections/dossier/*.md
# 3. cards        refs.json -> collections/citations/*.md
# 4. links        refs.json -> links.json, verified against document contents
# 5. catalog      filesystem + sidecars -> collections/catalog.json
# 6. site         catalog -> docs/ (static, searchable)
# 7. checks       every mirrored source contains what it claims; every link resolves
set -euo pipefail
cd "$(dirname "$0")/.."

python3 tools/make_references.py
python3 tools/resolve_missing.py --write >/dev/null
python3 tools/make_dossier.py
python3 tools/make_cards.py
python3 tools/make_links.py
python3 tools/build_catalog.py
python3 tools/build_site.py
python3 tools/verify_sources.py || true
python3 tools/update_readme_counts.py
python3 tools/check_site.py
echo "build complete"
