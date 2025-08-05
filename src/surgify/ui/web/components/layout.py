"""
Clean Layout System

Minimal, efficient page layouts with lazy loading
"""

from fastapi import Request
from fastapi.responses import HTMLResponse


def create_page(
    title: str, content: str, request: Request, page_type: str = "default"
) -> HTMLResponse:
    """Create a clean, minimal page layout"""

    # Get base CSS and JS based on page type
    assets = get_page_assets(page_type)

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#2563eb">
    <title>{title}</title>
    
    <!-- Essential CSS -->
    <link rel="stylesheet" href="/static/css/core.css">
    {assets['css']}
    
    <!-- PWA -->
    <link rel="manifest" href="/static/manifest.json">
    <link rel="icon" href="/static/icons/favicon.ico">
</head>
<body class="page-{page_type}">
    <!-- Navigation -->
    {create_nav(page_type)}
    
    <!-- Main Content -->
    <main class="main-content">
        {content}
    </main>
    
    <!-- Footer -->
    {create_footer()}
    
    <!-- Essential JS -->
    <script src="/static/js/core.js" defer></script>
    {assets['js']}
</body>
</html>
    """

    return HTMLResponse(content=html, status_code=200)


def create_nav(page_type: str = "default") -> str:
    """Create navigation based on page type"""

    if page_type == "auth":
        return """
        <nav class="nav-minimal">
            <a href="/web/" class="nav-brand">YAZ</a>
        </nav>
        """

    return """
    <nav class="nav-main">
        <div class="nav-container">
            <a href="/web/" class="nav-brand">YAZ Surgery Analytics</a>
            <div class="nav-links">
                <a href="/web/dashboard">Dashboard</a>
                <a href="/web/dashboard/clinical">Clinical</a>
                <a href="/web/dashboard/cases">Cases</a>
                <a href="/web/auth/logout">Logout</a>
            </div>
        </div>
    </nav>
    """


def create_footer() -> str:
    """Create minimal footer"""
    return """
    <footer class="footer-minimal">
        <p>&copy; 2025 YAZ Surgery Analytics</p>
    </footer>
    """


def get_page_assets(page_type: str) -> dict:
    """Get CSS and JS assets for specific page types"""

    assets = {
        "default": {"css": "", "js": ""},
        "auth": {
            "css": '<link rel="stylesheet" href="/static/css/auth.css">',
            "js": '<script src="/static/js/auth.js" defer></script>',
        },
        "dashboard": {
            "css": '<link rel="stylesheet" href="/static/css/dashboard.css">',
            "js": '<script src="/static/js/dashboard.js" defer></script>',
        },
        "clinical": {
            "css": '<link rel="stylesheet" href="/static/css/clinical.css">',
            "js": '<script src="/static/js/clinical.js" defer></script>',
        },
        "cases": {
            "css": '<link rel="stylesheet" href="/static/css/cases.css">',
            "js": '<script src="/static/js/cases.js" defer></script>',
        },
        "analytics": {
            "css": '<link rel="stylesheet" href="/static/css/analytics.css">',
            "js": '<script src="/static/js/analytics.js" defer></script>',
        },
    }

    return assets.get(page_type, assets["default"])
