"""
Home page for the Gastric ADCI Platform
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from features.auth.service import get_current_user, optional_user
from web.components.layout import create_base_layout

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, current_user = Depends(optional_user)):
    """Home page with platform overview and key metrics"""
    
    from fasthtml.common import *
    
    content = Div(
        # Hero section
        Div(
            Div(
                H1(
                    "Gastric ADCI Platform",
                    class_="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl"
                ),
                P(
                    "Evidence-based decision support for gastric oncology and surgery.",
                    class_="mt-3 text-base text-gray-500 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl"
                ),
                Div(
                    A(
                        "Get Started",
                        href="/cases/new",
                        class_="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10"
                    ) if current_user else A(
                        "Sign In",
                        href="/auth/login",
                        class_="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10"
                    ),
                    A(
                        "Learn More",
                        href="#features",
                        class_="w-full flex items-center justify-center px-8 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-gray-100 hover:bg-gray-200 md:py-4 md:text-lg md:px-10 ml-3"
                    ),
                    class_="mt-5 sm:mt-8 sm:flex sm:justify-center"
                ),
                class_="text-center"
            ),
            class_="py-12 bg-white"
        ),
        
        # Features section
        Div(
            Div(
                H2(
                    "Evidence-based decision support",
                    id="features",
                    class_="text-3xl font-extrabold text-gray-900 sm:text-4xl"
                ),
                P(
                    "The Gastric ADCI Platform integrates clinical data, precision decision algorithms, and evidence synthesis to support optimal treatment planning.",
                    class_="mt-4 max-w-2xl text-xl text-gray-500"
                ),
                class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center"
            ),
            Div(
                Div(
                    Div(
                        # Feature 1
                        Div(
                            Div(
                                Svg(
                                    Path(d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z"),
                                    Path(d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0"),
                                    class_="h-6 w-6 text-blue-600",
                                    stroke="currentColor",
                                    stroke_width="2",
                                    fill="none",
                                    viewBox="0 0 24 24"
                                ),
                                class_="flex items-center justify-center h-12 w-12 rounded-md bg-blue-100 text-blue-600"
                            ),
                            H3(
                                "ADCI Framework",
                                class_="mt-6 text-lg font-medium text-gray-900"
                            ),
                            P(
                                "Adaptive Decision Confidence Index provides quantified confidence scores for clinical recommendations.",
                                class_="mt-2 text-base text-gray-500"
                            ),
                            class_="p-6 bg-white rounded-lg border border-gray-200 shadow-md"
                        ),
                        
                        # Feature 2
                        Div(
                            Div(
                                Svg(
                                    Path(d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"),
                                    class_="h-6 w-6 text-blue-600",
                                    stroke="currentColor",
                                    stroke_width="2",
                                    fill="none",
                                    viewBox="0 0 24 24"
                                ),
                                class_="flex items-center justify-center h-12 w-12 rounded-md bg-blue-100 text-blue-600"
                            ),
                            H3(
                                "Markov Modeling",
                                class_="mt-6 text-lg font-medium text-gray-900"
                            ),
                            P(
                                "Advanced Markov chain simulations to predict disease progression and treatment outcomes.",
                                class_="mt-2 text-base text-gray-500"
                            ),
                            class_="p-6 bg-white rounded-lg border border-gray-200 shadow-md"
                        ),
                        
                        # Feature 3
                        Div(
                            Div(
                                Svg(
                                    Path(d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"),
                                    class_="h-6 w-6 text-blue-600",
                                    stroke="currentColor",
                                    stroke_width="2",
                                    fill="none",
                                    viewBox="0 0 24 24"
                                ),
                                class_="flex items-center justify-center h-12 w-12 rounded-md bg-blue-100 text-blue-600"
                            ),
                            H3(
                                "Evidence Synthesis",
                                class_="mt-6 text-lg font-medium text-gray-900"
                            ),
                            P(
                                "Integrates clinical guidelines, literature, and real-world evidence for informed decision making.",
                                class_="mt-2 text-base text-gray-500"
                            ),
                            class_="p-6 bg-white rounded-lg border border-gray-200 shadow-md"
                        ),
                        
                        # Feature 4
                        Div(
                            Div(
                                Svg(
                                    Path(d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2"),
                                    class_="h-6 w-6 text-blue-600",
                                    stroke="currentColor",
                                    stroke_width="2",
                                    fill="none",
                                    viewBox="0 0 24 24"
                                ),
                                class_="flex items-center justify-center h-12 w-12 rounded-md bg-blue-100 text-blue-600"
                            ),
                            H3(
                                "HIPAA & GDPR Compliant",
                                class_="mt-6 text-lg font-medium text-gray-900"
                            ),
                            P(
                                "Enterprise-grade security with full audit trails and role-based access control.",
                                class_="mt-2 text-base text-gray-500"
                            ),
                            class_="p-6 bg-white rounded-lg border border-gray-200 shadow-md"
                        ),
                        
                        # Feature 5 - Education Module
                        Div(
                            Div(
                                Svg(
                                    Path(d="M12 14l9-5-9-5-9 5 9 5z"),
                                    Path(d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"),
                                    Path(stroke_linecap="round", stroke_linejoin="round", stroke_width="2", d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"),
                                    class_="h-6 w-6 text-green-600",
                                    stroke="currentColor",
                                    stroke_width="2",
                                    fill="none",
                                    viewBox="0 0 24 24"
                                ),
                                class_="flex items-center justify-center h-12 w-12 rounded-md bg-green-100 text-green-600"
                            ),
                            H3(
                                A(
                                    "Medical Education",
                                    href="/education",
                                    class_="mt-6 text-lg font-medium text-gray-900 hover:text-green-600"
                                )
                            ),
                            P(
                                "Comprehensive training programs, skill assessment, and continuing education for surgical excellence.",
                                class_="mt-2 text-base text-gray-500"
                            ),
                            A(
                                "Explore Education →",
                                href="/education",
                                class_="mt-3 text-sm font-medium text-green-600 hover:text-green-500"
                            ),
                            class_="p-6 bg-white rounded-lg border border-gray-200 shadow-md hover:shadow-lg transition-shadow"
                        ),
                        
                        # Feature 6 - Hospitality Module
                        Div(
                            Div(
                                Svg(
                                    Path(d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"),
                                    class_="h-6 w-6 text-pink-600",
                                    stroke="currentColor",
                                    stroke_width="2",
                                    fill="none",
                                    viewBox="0 0 24 24"
                                ),
                                class_="flex items-center justify-center h-12 w-12 rounded-md bg-pink-100 text-pink-600"
                            ),
                            H3(
                                A(
                                    "Patient Hospitality",
                                    href="/hospitality",
                                    class_="mt-6 text-lg font-medium text-gray-900 hover:text-pink-600"
                                )
                            ),
                            P(
                                "Comprehensive patient care coordination, family support, and hospitality management services.",
                                class_="mt-2 text-base text-gray-500"
                            ),
                            A(
                                "Explore Hospitality →",
                                href="/hospitality",
                                class_="mt-3 text-sm font-medium text-pink-600 hover:text-pink-500"
                            ),
                            class_="p-6 bg-white rounded-lg border border-gray-200 shadow-md hover:shadow-lg transition-shadow"
                        ),
                        
                        class_="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3"
                    ),
                    class_="mt-12"
                ),
                class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12"
            ),
            class_="bg-gray-50"
        ),
        
        # Call to action
        Div(
            Div(
                H2(
                    "Ready to improve your clinical decision making?",
                    class_="text-3xl font-extrabold tracking-tight text-white sm:text-4xl"
                ),
                P(
                    "Start using the Gastric ADCI Platform today for evidence-based decision support in gastric oncology and surgery.",
                    class_="mt-3 text-lg text-blue-100 max-w-3xl"
                ),
                Div(
                    A(
                        "Sign Up",
                        href="/auth/register",
                        class_="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-blue-700 bg-white hover:bg-blue-50"
                    ),
                    A(
                        "Contact Us",
                        href="/contact",
                        class_="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-800 hover:bg-blue-700 ml-4"
                    ),
                    class_="mt-8 flex flex-col sm:flex-row gap-4 sm:gap-0"
                ),
                class_="max-w-7xl mx-auto text-center py-16 px-4 sm:py-20 sm:px-6 lg:px-8"
            ),
            class_="bg-blue-600"
        ),
        id="main-content"
    )
    
    return create_base_layout(
        title="Home",
        content=content,
        user=current_user
    )
