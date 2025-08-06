#!/bin/bash
# Bundle Size Analysis for Surgify PWA

echo "=== Surgify PWA Bundle Analysis ===" 
echo "Generated: $(date)"
echo ""

echo "📦 UNCOMPRESSED SIZES:"
echo "JavaScript:"
du -h /workspaces/yaz/src/surgify/ui/web/static/js/app.js | awk '{print "  app.js: " $1}'

echo "CSS:"
du -h /workspaces/yaz/src/surgify/ui/web/static/css/main.css | awk '{print "  main.css: " $1}'
du -h /workspaces/yaz/src/surgify/ui/web/static/css/tailwind.css | awk '{print "  tailwind.css: " $1}'

echo ""
echo "🗜️  GZIPPED SIZES:"
JS_GZIP=$(gzip -c /workspaces/yaz/src/surgify/ui/web/static/js/app.js | wc -c)
CSS_MAIN_GZIP=$(gzip -c /workspaces/yaz/src/surgify/ui/web/static/css/main.css | wc -c)
CSS_TW_GZIP=$(gzip -c /workspaces/yaz/src/surgify/ui/web/static/css/tailwind.css | wc -c)

echo "  app.js: ${JS_GZIP} bytes ($(echo "scale=1; $JS_GZIP/1024" | bc)KB)"
echo "  main.css: ${CSS_MAIN_GZIP} bytes ($(echo "scale=1; $CSS_MAIN_GZIP/1024" | bc)KB)"
echo "  tailwind.css: ${CSS_TW_GZIP} bytes ($(echo "scale=1; $CSS_TW_GZIP/1024" | bc)KB)"

TOTAL_GZIP=$((JS_GZIP + CSS_MAIN_GZIP + CSS_TW_GZIP))
echo ""
echo "📊 TOTAL GZIPPED: ${TOTAL_GZIP} bytes ($(echo "scale=1; $TOTAL_GZIP/1024" | bc)KB)"
echo ""

if [ $TOTAL_GZIP -lt 14336 ]; then
    echo "✅ UNDER 14KB TARGET - Excellent!"
else
    echo "❌ OVER 14KB TARGET - Optimization needed"
fi

echo ""
echo "🔍 TOP CONTRIBUTORS:"
echo "1. Vanilla JavaScript PWA implementation"
echo "2. Tailwind CSS (minimal build)"
echo "3. Service Worker caching"
echo "4. PWA manifest and icons"
