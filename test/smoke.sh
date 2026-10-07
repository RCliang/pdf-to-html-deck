#!/usr/bin/env bash
# 冒烟测试:fixture → init → extract → build(默认+主题)→ 断言产物
# 运行: bash test/smoke.sh   (需 node>=18、python3+pypdf)
set -euo pipefail

PKG_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CLI="$PKG_DIR/bin/cli.js"
TMP="$(mktemp -d)/demo"
trap 'echo "smoke workspace: $TMP"' EXIT

echo "== 1. init =="
node "$CLI" init --dir "$TMP" --title "Fixture Book · Smoke"

echo "== 2. extract =="
node "$CLI" extract "$PKG_DIR/test/fixture.pdf" --dir "$TMP" >/dev/null
test -f "$TMP/work/manifest.json" || { echo "manifest missing"; exit 1; }
test -f "$TMP/work/text/ch03.txt" || { echo "ch03 missing"; exit 1; }
grep -q "Chapter Two" "$TMP/work/text/ch03.txt" || { echo "ch03 content mismatch"; exit 1; }
grep -q '"part": "I Basics"' "$TMP/work/manifest.json" || { echo "part not detected"; exit 1; }

echo "== 3. 片段 + 组装(默认主题) =="
cat > "$TMP/work/fragments/cov.html" <<'HTML'
<section class="slide" id="smoke-cov" data-part="0" data-crumb="SMOKE" data-title="Cover">
  <header class="s-head"><h2 class="k-h">Smoke <em>Test</em></h2></header>
</section>
HTML
printf 'cov\n' > "$TMP/work/order.txt"
node "$CLI" build --dir "$TMP"
grep -q 'id="smoke-cov"' "$TMP/index.html" || { echo "section missing in index"; exit 1; }
grep -q 'Fixture Book · Smoke' "$TMP/index.html" || { echo "title placeholder not replaced"; exit 1; }

echo "== 4. 主题切换与解除 =="
node "$CLI" build --dir "$TMP" --theme apple-light >/dev/null
grep -q 'data-theme="apple-light"' "$TMP/index.html" || { echo "theme not injected"; exit 1; }
node "$CLI" build --dir "$TMP" --theme none >/dev/null
! grep -q 'data-theme=' "$TMP/index.html" || { echo "theme not removed"; exit 1; }

echo "== 5. theme list / deploy / usage =="
node "$CLI" theme list | grep -q chalkboard || { echo "theme list broken"; exit 1; }
node "$CLI" deploy --dir "$TMP" >/dev/null
test -f "$TMP/.github/workflows/deploy.yml" || { echo "deploy yml missing"; exit 1; }
node "$CLI" 2>&1 | grep -q "init" || { echo "usage broken"; exit 1; }

echo
echo "SMOKE-OK ✅  (6 页 fixture → 3 章 manifest → 组装/主题/部署 全链路通过)"
