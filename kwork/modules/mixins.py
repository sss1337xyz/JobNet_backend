from django.http import JsonResponse

from kwork.models import ClientSession


# Коды которые начинаются с 4000 это ошибки авторизации
class AuthMixin:
    def dispatch(self, request, *args, **kwargs):
        session_key = request.GET.get('session_key')
        if not session_key:
            return JsonResponse({'error': "Session key is empty", 'code': 4001}, status=400)
        try:
            session = ClientSession.objects.get(session_key=session_key)
            if not session.user_id:
                return JsonResponse({'error': "The session does not belong to the user", 'code': 4003}, status=400)
        except Exception as e:
            return JsonResponse({'error': "Session key is invalid", 'code': 4002}, status=400)
        return super().dispatch(request, *args, **kwargs)