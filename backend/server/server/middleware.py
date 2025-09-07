import jwt
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime, timezone

class JWTAuthenticationMiddleware:
    """
    Middleware to validate JWT token in Authorization header.
    If valid, attach user_id to request.
    If invalid, reject the request.
    Skips authentication for login endpoint.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip authentication for login and other public endpoints
        public_paths = ["/api/employees/login/"]  # Add more paths if needed
        if request.path.startswith("/api/") and request.path not in public_paths:
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return JsonResponse({"error": "Authorization header missing"}, status=401)

            try:
                # Expecting 'Bearer <token>'
                token_type, token = auth_header.split()
                if token_type.lower() != "bearer":
                    raise ValueError("Invalid token type")
                
                # Decode JWT
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                
                # Check expiration manually
                exp = payload.get("exp")
                if exp is None or datetime.now(timezone.utc).timestamp() > exp:
                    return JsonResponse({"error": "Token has expired"}, status=401)

                # Attach user_id to request for views
                request.user_id = payload.get("employee_id")

            except (jwt.ExpiredSignatureError, jwt.DecodeError, ValueError) as e:
                return JsonResponse({"error": f"Invalid token: {str(e)}"}, status=401)

        response = self.get_response(request)
        return response