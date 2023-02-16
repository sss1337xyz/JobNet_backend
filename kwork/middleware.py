from django.http import JsonResponse

from kwork.models import ClientSession


# Коды начинающиеся с 4*** это ошибки с авторизацией
class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Применить нужную логику для URL-адресов, начинающихся с /api/
        if request.path.startswith('/api/'):
            session_key = request.GET.get('session_key')
            if not session_key:
                return JsonResponse({'error': "Session key is empty", 'code': 4001}, status=400)
            try:
                session = ClientSession.objects.get(session_key=session_key)
                if not session.user_id:
                    return JsonResponse({'error': "The session does not belong to the user", 'code': 4003}, status=400)
            except Exception as e:
                return JsonResponse({'error': "Session key is invalid", 'code': 4002}, status=400)

        response = self.get_response(request)
        return response
