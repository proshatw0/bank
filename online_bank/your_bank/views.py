from urllib.parse import urlparse
from django.shortcuts import render, redirect
from django.contrib.auth.models import AnonymousUser


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