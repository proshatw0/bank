from urllib.parse import urlparse
from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session
from django.utils import timezone

def remove_field_from_user_sessions(user_id, field_name):
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in sessions:
        data = session.get_decoded()
        if str(user_id) == str(data.get('_auth_user_id')):
            if field_name in data:
                del data[field_name]
                session.session_data = Session.objects.encode(data)
                session.save()


def go_pin(request):
    if request.user.is_authenticated:
        next_url = request.GET.get('next', '/login/pin-code/')
        return redirect(next_url)
    else:
        next_url = request.GET.get('next', '/login/')
        return redirect(next_url)
    
def bank_view(request):
    return render(request, 'your_bank.html')

def your_bank_view(request):
    remove_field_from_user_sessions(request.user.id, 'redirect_url')
    referer = request.META.get('HTTP_REFERER')
    if referer:
        parsed_referer = urlparse(referer)
        current_domain = request.get_host()
        
        if parsed_referer.netloc == current_domain:
            return bank_view(request)
        else:
            print(456)
            return go_pin(request)
    else:
        return go_pin(request)