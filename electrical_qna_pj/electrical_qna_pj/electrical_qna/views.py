from django.shortcuts import redirect

def root_redirect(request):
    return redirect('ask_question')  # Redirect root URL to ask_question view
