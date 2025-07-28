"""
Base layout component for consistent page structure
"""

from fasthtml.common import *


def create_base_layout(title: str, content, user: dict = None):
    """Create base layout with navigation and PWA features"""
    
    return Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Meta(name="theme-color", content="#2563eb"),
            Meta(name="description", content="Gastric Oncology-Surgery Decision Support Platform"),
            Title(title),
            
            # PWA manifest
            Link(rel="manifest", href="/manifest.json"),
            
            # Icons
            Link(rel="icon", type_="image/x-icon", href="/static/favicon.ico"),
            Link(rel="apple-touch-icon", href="/static/icons/apple-touch-icon.png"),
            
            # CSS
            Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"),
            Link(rel="stylesheet", href="/static/css/app.css"),
            
            # HTMX
            Script(src="https://unpkg.com/htmx.org@1.9.6/dist/htmx.min.js"),
            Script(src="https://unpkg.com/htmx.org@1.9.6/dist/ext/response-targets.js"),
            Script(src="https://unpkg.com/htmx.org@1.9.6/dist/ext/loading-states.js"),
            
            # Gun.js
            Script(src="https://cdn.jsdelivr.net/npm/gun/gun.js"),
            Script(src="https://cdn.jsdelivr.net/npm/gun/sea.js"),
            
            # Chart.js
            Script(src="https://cdn.jsdelivr.net/npm/chart.js"),
            
            # Alpine.js
            Script(src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js", defer=True),
        ),
        Body(
            # Navigation
            create_navigation(user),
            
            # Main content
            Main(
                content,
                id="main-content",
                class_="flex-1"
            ),
            
            # Footer
            create_footer(),
            
            # PWA install prompt
            create_pwa_install_prompt(),
            
            # Application scripts
            Script(src="/static/js/app.js"),
            Script(src="/static/js/gun-integration.js"),
            Script(src="/static/js/pwa.js"),
            
            class_="min-h-screen bg-gray-50 flex flex-col",
            **{"hx-ext": "response-targets,loading-states"}
        ),
        lang="en"
    )


def create_navigation(user: dict = None):
    """Create responsive navigation bar"""
    
    return Nav(
        Div(
            # Logo and brand
            Div(
                A(
                    Div(
                        # Medical cross icon
                        Svg(
                            Path(d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.58L19 8l-9 9z", 
                                 fill="currentColor"),
                            class_="w-8 h-8 text-blue-600",
                            viewBox="0 0 24 24"
                        ),
                        Span(
                            Span("Gastric ADCI", class_="font-bold text-gray-900"),
                            Span("Platform", class_="font-normal text-gray-600 ml-1"),
                            class_="text-xl"
                        ),
                        class_="flex items-center space-x-3"
                    ),
                    href="/",
                    class_="flex items-center"
                ),
                class_="flex items-center"
            ),
            
            # Desktop navigation
            Div(
                *create_nav_links(user),
                class_="hidden md:flex md:space-x-8"
            ),
            
            # User menu and mobile toggle
            Div(
                # User menu (desktop)
                create_user_menu(user) if user else create_auth_buttons(),
                
                # Mobile menu button
                Button(
                    Svg(
                        Path(stroke="currentColor", stroke_linecap="round", stroke_linejoin="round", stroke_width="2", 
                             d="M4 6h16M4 12h16M4 18h16"),
                        class_="w-6 h-6",
                        fill="none",
                        viewBox="0 0 24 24"
                    ),
                    class_="md:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500",
                    id="mobile-menu-button",
                    **{"@click": "mobileMenuOpen = !mobileMenuOpen"}
                ),
                
                class_="flex items-center space-x-4"
            ),
            
            class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center h-16"
        ),
        
        # Mobile navigation menu
        Div(
            Div(
                *create_nav_links(user, mobile=True),
                create_mobile_user_section(user),
                class_="px-2 pt-2 pb-3 space-y-1 sm:px-3"
            ),
            class_="md:hidden",
            id="mobile-menu",
            **{"x-show": "mobileMenuOpen", "x-transition": True}
        ),
        
        class_="bg-white shadow-sm sticky top-0 z-50",
        **{"x-data": "{ mobileMenuOpen: false }"}
    )


def create_nav_links(user: dict = None, mobile: bool = False):
    """Create navigation links"""
    
    base_class = "text-gray-900 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
    mobile_class = "text-gray-900 hover:text-blue-600 block px-3 py-2 rounded-md text-base font-medium"
    
    link_class = mobile_class if mobile else base_class
    
    links = [
        A("Home", href="/", class_=link_class),
        A("Protocols", href="/protocols", class_=link_class) if user else None,
        A("Decision Support", href="/decision-support", class_=link_class) if user and user.get("role") in ["practitioner", "researcher"] else None,
        A("Cohort Management", href="/cohorts", class_=link_class) if user and user.get("role") in ["researcher", "practitioner"] else None,
        A("About", href="/about", class_=link_class),
    ]
    
    return [link for link in links if link is not None]


def create_user_menu(user: dict):
    """Create user dropdown menu for desktop"""
    
    return Div(
        Button(
            Div(
                Img(
                    src=f"https://ui-avatars.com/api/?name={user.get('first_name', '')}+{user.get('last_name', '')}&background=2563eb&color=fff",
                    alt="Profile",
                    class_="w-8 h-8 rounded-full"
                ),
                Span(f"{user.get('first_name', '')} {user.get('last_name', '')}", class_="ml-3 text-sm font-medium text-gray-700"),
                Svg(
                    Path(stroke="currentColor", stroke_linecap="round", stroke_linejoin="round", stroke_width="2", d="M19 9l-7 7-7-7"),
                    class_="ml-2 w-4 h-4 text-gray-400",
                    fill="none",
                    viewBox="0 0 24 24"
                ),
                class_="flex items-center"
            ),
            class_="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500",
            **{"@click": "userMenuOpen = !userMenuOpen"}
        ),
        
        # Dropdown menu
        Div(
            Div(
                A(
                    "Profile",
                    href="/profile",
                    class_="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                ),
                A(
                    "Settings", 
                    href="/settings",
                    class_="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                ),
                Hr(class_="my-1"),
                A(
                    "Sign out",
                    href="/auth/logout",
                    class_="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                ),
                class_="py-1"
            ),
            class_="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5",
            **{"x-show": "userMenuOpen", "x-transition": True, "@click.away": "userMenuOpen = false"}
        ),
        
        class_="relative",
        **{"x-data": "{ userMenuOpen: false }"}
    )


def create_auth_buttons():
    """Create authentication buttons for non-logged-in users"""
    
    return Div(
        A(
            "Sign in",
            href="/auth/login",
            class_="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
        ),
        A(
            "Get started",
            href="/auth/register",
            class_="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
        ),
        class_="flex items-center space-x-4"
    )


def create_mobile_user_section(user: dict = None):
    """Create mobile user section"""
    
    if not user:
        return Div(
            Hr(class_="my-3"),
            A(
                "Sign in",
                href="/auth/login", 
                class_="block px-3 py-2 rounded-md text-base font-medium text-gray-900 hover:text-blue-600"
            ),
            A(
                "Get started",
                href="/auth/register",
                class_="block px-3 py-2 rounded-md text-base font-medium bg-blue-600 text-white hover:bg-blue-700"
            )
        )
    
    return Div(
        Hr(class_="my-3"),
        Div(
            Div(
                Img(
                    src=f"https://ui-avatars.com/api/?name={user.get('first_name', '')}+{user.get('last_name', '')}&background=2563eb&color=fff",
                    alt="Profile",
                    class_="w-10 h-10 rounded-full"
                ),
                Div(
                    Div(f"{user.get('first_name', '')} {user.get('last_name', '')}", class_="text-base font-medium text-gray-900"),
                    Div(user.get('email', ''), class_="text-sm text-gray-500"),
                    class_="ml-3"
                ),
                class_="flex items-center px-3 py-2"
            ),
            A(
                "Profile",
                href="/profile",
                class_="block px-3 py-2 rounded-md text-base font-medium text-gray-900 hover:text-blue-600"
            ),
            A(
                "Settings",
                href="/settings", 
                class_="block px-3 py-2 rounded-md text-base font-medium text-gray-900 hover:text-blue-600"
            ),
            A(
                "Sign out",
                href="/auth/logout",
                class_="block px-3 py-2 rounded-md text-base font-medium text-gray-900 hover:text-blue-600"
            )
        )
    )


def create_footer():
    """Create application footer"""
    
    return Footer(
        Div(
            Div(
                # Company info
                Div(
                    H3("Gastric ADCI Platform", class_="text-sm font-semibold text-gray-900 tracking-wider uppercase"),
                    P(
                        "Evidence-based decision support for gastric oncology and surgery.",
                        class_="mt-4 text-base text-gray-500"
                    ),
                    class_="col-span-1 md:col-span-2"
                ),
                
                # Links
                Div(
                    H3("Platform", class_="text-sm font-semibold text-gray-900 tracking-wider uppercase"),
                    Ul(
                        Li(A("Clinical Protocols", href="/protocols", class_="text-base text-gray-500 hover:text-gray-900")),
                        Li(A("Decision Support", href="/decision-support", class_="text-base text-gray-500 hover:text-gray-900")),
                        Li(A("Evidence Database", href="/evidence", class_="text-base text-gray-500 hover:text-gray-900")),
                        class_="mt-4 space-y-4"
                    )
                ),
                
                # Support
                Div(
                    H3("Support", class_="text-sm font-semibold text-gray-900 tracking-wider uppercase"),
                    Ul(
                        Li(A("Documentation", href="/docs", class_="text-base text-gray-500 hover:text-gray-900")),
                        Li(A("Clinical Support", href="mailto:clinical-support@gastric-adci.health", class_="text-base text-gray-500 hover:text-gray-900")),
                        Li(A("Technical Support", href="mailto:tech-support@gastric-adci.health", class_="text-base text-gray-500 hover:text-gray-900")),
                        class_="mt-4 space-y-4"
                    )
                ),
                
                # Legal
                Div(
                    H3("Legal", class_="text-sm font-semibold text-gray-900 tracking-wider uppercase"),
                    Ul(
                        Li(A("Privacy Policy", href="/privacy", class_="text-base text-gray-500 hover:text-gray-900")),
                        Li(A("Terms of Service", href="/terms", class_="text-base text-gray-500 hover:text-gray-900")),
                        Li(A("HIPAA Compliance", href="/hipaa", class_="text-base text-gray-500 hover:text-gray-900")),
                        class_="mt-4 space-y-4"
                    )
                ),
                
                class_="grid grid-cols-1 md:grid-cols-4 gap-8"
            ),
            
            # Bottom section
            Div(
                Div(
                    P(
                        "© 2024 Gastric ADCI Platform. All rights reserved.",
                        class_="text-base text-gray-500"
                    ),
                    P(
                        "⚠️ For clinical decision support only. Not a substitute for professional medical judgment.",
                        class_="text-sm text-yellow-600 mt-2"
                    )
                ),
                class_="border-t border-gray-200 pt-8"
            ),
            
            class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12"
        ),
        class_="bg-white border-t border-gray-200 mt-auto"
    )


def create_pwa_install_prompt():
    """Create PWA installation prompt"""
    
    return Div(
        Div(
            Div(
                Svg(
                    Path(d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z",
                         fill="currentColor"),
                    class_="w-6 h-6 text-blue-600",
                    viewBox="0 0 24 24"
                ),
                Div(
                    H4("Install Gastric ADCI App", class_="text-lg font-medium text-gray-900"),
                    P("Get the full experience with offline access and push notifications.", 
                      class_="text-sm text-gray-500"),
                    class_="ml-3 flex-1"
                ),
                class_="flex items-start"
            ),
            Div(
                Button(
                    "Install",
                    id="pwa-install-button",
                    class_="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium mr-3"
                ),
                Button(
                    "✕",
                    **{"@click": "showInstallPrompt = false"},
                    class_="text-gray-400 hover:text-gray-600 p-1"
                ),
                class_="flex items-center"
            ),
            class_="flex justify-between items-start p-4"
        ),
        id="pwa-install-prompt",
        class_="fixed bottom-4 left-4 right-4 md:left-auto md:w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-50",
        **{
            "x-show": "showInstallPrompt && !isPWAInstalled",
            "x-transition": True,
            "x-data": "{ showInstallPrompt: false, isPWAInstalled: false }"
        }
    )
