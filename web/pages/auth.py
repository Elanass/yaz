"""
Authentication pages for the Gastric ADCI Platform
"""

from fastapi import APIRouter as FastAPIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional, Dict, Any
from fasthtml.common import Div, H1, H2, H3, H4, P, Form as FHTMLForm, Input, Button, A, Br, Script, Nav, Footer

from core.dependencies import get_current_user, optional_user
from web.components.layout import create_base_layout

router = FastAPIRouter(prefix="/auth")

@router.get("/login")
async def login_page(request: Request, next: Optional[str] = None, current_user = Depends(optional_user)):
    """Login page"""
    
    # Redirect if already logged in
    if current_user:
        return RedirectResponse(url=next or "/", status_code=303)
    
    content = Div(
        Div(
            H2("Sign in to your account", class_="mt-6 text-center text-3xl font-extrabold text-gray-900"),
            P(
                "Or ",
                A("register for a new account", href="/auth/register", class_="font-medium text-blue-600 hover:text-blue-500"),
                class_="mt-2 text-center text-sm text-gray-600"
            ),
        ),
        Div(
            Div(
                Form(
                    Div(
                        Div(
                            Label("Email address", for_="email", class_="block text-sm font-medium text-gray-700"),
                            Div(
                                Input(
                                    type_="email",
                                    name="email",
                                    id="email",
                                    autocomplete="email",
                                    required=True,
                                    class_="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                ),
                                class_="mt-1"
                            ),
                        ),
                        class_="mb-4"
                    ),
                    Div(
                        Div(
                            Label("Password", for_="password", class_="block text-sm font-medium text-gray-700"),
                            Div(
                                Input(
                                    type_="password",
                                    name="password",
                                    id="password",
                                    autocomplete="current-password",
                                    required=True,
                                    class_="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                ),
                                class_="mt-1"
                            ),
                        ),
                        class_="mb-4"
                    ),
                    Div(
                        Div(
                            Input(
                                id="remember-me",
                                name="remember-me",
                                type_="checkbox",
                                class_="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            ),
                            Label(
                                "Remember me",
                                for_="remember-me",
                                class_="ml-2 block text-sm text-gray-900"
                            ),
                            class_="flex items-center"
                        ),
                        Div(
                            A(
                                "Forgot your password?",
                                href="/auth/reset-password",
                                class_="font-medium text-blue-600 hover:text-blue-500"
                            ),
                            class_="text-sm"
                        ),
                        class_="flex items-center justify-between"
                    ),
                    Div(
                        Button(
                            "Sign in",
                            type_="submit",
                            class_="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        ),
                        class_="mt-6"
                    ),
                    # Error message placeholder
                    Div(
                        id="login-error",
                        class_="mt-3 text-sm text-red-600 hidden"
                    ),
                    Input(type_="hidden", name="next", value=next or "/") if next else "",
                    method="post",
                    action="/api/v1/auth/login",
                    id="login-form",
                    **{
                        "hx-post": "/api/v1/auth/login",
                        "hx-target": "#login-error",
                        "hx-swap": "innerHTML",
                        "hx-trigger": "submit",
                        "hx-redirect": "true"
                    }
                ),
                class_="mt-8 sm:mx-auto sm:w-full sm:max-w-md"
            ),
            class_="py-8 px-4 sm:px-10 bg-white sm:rounded-lg sm:shadow"
        ),
        class_="min-h-full flex flex-col justify-center py-12 sm:px-6 lg:px-8 max-w-md mx-auto"
    )
    
    return create_base_layout(
        title="Sign In",
        content=content,
        user=None
    )

@router.get("/register")
async def register_page(request: Request, current_user = Depends(optional_user)):
    """Registration page"""
    
    # Redirect if already logged in
    if current_user:
        return RedirectResponse(url="/", status_code=303)
    
    content = Div(
        Div(
            H2("Create a new account", class_="mt-6 text-center text-3xl font-extrabold text-gray-900"),
            P(
                "Already have an account? ",
                A("Sign in", href="/auth/login", class_="font-medium text-blue-600 hover:text-blue-500"),
                class_="mt-2 text-center text-sm text-gray-600"
            ),
        ),
        Div(
            Div(
                Form(
                    Div(
                        Div(
                            Label("Full name", for_="name", class_="block text-sm font-medium text-gray-700"),
                            Div(
                                Input(
                                    type_="text",
                                    name="name",
                                    id="name",
                                    autocomplete="name",
                                    required=True,
                                    class_="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                ),
                                class_="mt-1"
                            ),
                        ),
                        class_="mb-4"
                    ),
                    Div(
                        Div(
                            Label("Email address", for_="email", class_="block text-sm font-medium text-gray-700"),
                            Div(
                                Input(
                                    type_="email",
                                    name="email",
                                    id="email",
                                    autocomplete="email",
                                    required=True,
                                    class_="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                ),
                                class_="mt-1"
                            ),
                        ),
                        class_="mb-4"
                    ),
                    Div(
                        Div(
                            Label("Password", for_="password", class_="block text-sm font-medium text-gray-700"),
                            Div(
                                Input(
                                    type_="password",
                                    name="password",
                                    id="password",
                                    autocomplete="new-password",
                                    required=True,
                                    class_="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                ),
                                class_="mt-1"
                            ),
                        ),
                        class_="mb-4"
                    ),
                    Div(
                        Div(
                            Label("Role", for_="role", class_="block text-sm font-medium text-gray-700"),
                            Div(
                                Select(
                                    Option("Select role", value="", disabled=True, selected=True),
                                    Option("Clinician", value="clinician"),
                                    Option("Researcher", value="researcher"),
                                    Option("Administrator", value="administrator"),
                                    name="role",
                                    id="role",
                                    required=True,
                                    class_="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                                ),
                                class_="mt-1"
                            ),
                        ),
                        class_="mb-4"
                    ),
                    Div(
                        Div(
                            Input(
                                id="terms",
                                name="terms",
                                type_="checkbox",
                                required=True,
                                class_="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            ),
                            Label(
                                Span("I agree to the "),
                                A(
                                    "terms and conditions",
                                    href="/terms",
                                    class_="font-medium text-blue-600 hover:text-blue-500"
                                ),
                                for_="terms",
                                class_="ml-2 block text-sm text-gray-900"
                            ),
                            class_="flex items-center"
                        ),
                        class_="mb-4"
                    ),
                    Div(
                        Button(
                            "Create account",
                            type_="submit",
                            class_="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        ),
                        class_="mt-6"
                    ),
                    # Error message placeholder
                    Div(
                        id="register-error",
                        class_="mt-3 text-sm text-red-600 hidden"
                    ),
                    method="post",
                    action="/api/v1/auth/register",
                    id="register-form",
                    **{
                        "hx-post": "/api/v1/auth/register",
                        "hx-target": "#register-error",
                        "hx-swap": "innerHTML",
                        "hx-trigger": "submit",
                        "hx-redirect": "true"
                    }
                ),
                class_="mt-8 sm:mx-auto sm:w-full sm:max-w-md"
            ),
            class_="py-8 px-4 sm:px-10 bg-white sm:rounded-lg sm:shadow"
        ),
        class_="min-h-full flex flex-col justify-center py-12 sm:px-6 lg:px-8 max-w-md mx-auto"
    )
    
    return create_base_layout(
        title="Register",
        content=content,
        user=None
    )

@router.get("/logout")
@router.post("/logout")
async def logout(request: Request):
    """Logout user"""
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response

@router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: Optional[str] = Form(None)
):
    """Handle login form submission"""
    
    # For demo purposes, accept any username/password
    # In production, this would validate against a database
    if username and password:
        # Create a mock response (in real app, this would call the auth API)
        response = RedirectResponse(url=next or "/", status_code=303)
        # Set demo cookies
        response.set_cookie("access_token", f"demo_token_{username}", httponly=True)
        return response
    else:
        # Return to login with error
        return RedirectResponse(url="/auth/login?error=invalid", status_code=303)

@router.get("/profile")
async def profile(request: Request, current_user = Depends(get_current_user)):
    """User profile page"""
    
    content = Div(
        H1("Your Profile", class_="text-2xl font-bold text-gray-900 mb-6"),
        
        Div(
            Div(
                Div(
                    Img(
                        src=current_user.get("avatar", "/static/avatars/default.png"),
                        alt="Profile",
                        class_="h-24 w-24 rounded-full"
                    ),
                    class_="flex-shrink-0"
                ),
                Div(
                    H2(current_user.get("name", "User"), class_="text-xl font-bold text-gray-900"),
                    P(current_user.get("email", ""), class_="text-gray-600"),
                    Div(
                        Span(
                            current_user.get("role", "User").capitalize(),
                            class_="px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                        ),
                        class_="mt-1"
                    ),
                    class_="ml-5"
                ),
                class_="flex items-center"
            ),
            class_="bg-white shadow overflow-hidden sm:rounded-lg p-6 mb-6"
        ),
        
        Div(
            H3("Account Information", class_="text-lg font-medium text-gray-900 mb-4"),
            Dl(
                Div(
                    Dt("Last login", class_="text-sm font-medium text-gray-500"),
                    Dd(current_user.get("last_login", "N/A"), class_="mt-1 text-sm text-gray-900"),
                    class_="sm:grid sm:grid-cols-3 sm:gap-4 py-3"
                ),
                Div(
                    Dt("Member since", class_="text-sm font-medium text-gray-500"),
                    Dd(current_user.get("created_at", "N/A"), class_="mt-1 text-sm text-gray-900"),
                    class_="sm:grid sm:grid-cols-3 sm:gap-4 py-3 border-t border-gray-200"
                ),
                Div(
                    Dt("Role", class_="text-sm font-medium text-gray-500"),
                    Dd(current_user.get("role", "User").capitalize(), class_="mt-1 text-sm text-gray-900"),
                    class_="sm:grid sm:grid-cols-3 sm:gap-4 py-3 border-t border-gray-200"
                ),
                Div(
                    Dt("Permissions", class_="text-sm font-medium text-gray-500"),
                    Dd(
                        Ul(
                            *[
                                Li(perm, class_="text-sm text-gray-900") 
                                for perm in current_user.get("permissions", [])
                            ],
                            class_="list-disc pl-5"
                        ),
                        class_="mt-1"
                    ),
                    class_="sm:grid sm:grid-cols-3 sm:gap-4 py-3 border-t border-gray-200"
                ),
                class_="mt-4"
            ),
            class_="bg-white shadow overflow-hidden sm:rounded-lg p-6 mb-6"
        ),
        
        Div(
            H3("Actions", class_="text-lg font-medium text-gray-900 mb-4"),
            Div(
                A(
                    "Edit Profile",
                    href="/auth/profile/edit",
                    class_="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                ),
                A(
                    "Change Password",
                    href="/auth/change-password",
                    class_="ml-3 inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                ),
                class_="flex space-x-2"
            ),
            class_="bg-white shadow overflow-hidden sm:rounded-lg p-6"
        ),
        
        id="main-content",
        class_="container mx-auto px-4 py-8 max-w-3xl"
    )
    
    return create_base_layout(
        title="Your Profile",
        content=content,
        user=current_user
    )
