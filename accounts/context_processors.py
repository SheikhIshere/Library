from django.contrib.auth.models import User
from .models import ProfileModel   # adjust if your Profile is in another app
from .utils import format_tokens

def user_balance(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        
        formated_balance = format_tokens(request.user.profile.balance)

        return{
            "user_balance": formated_balance,
            "user_profile": request.user.profile
        }
    return {
        "user_balance": format_tokens(0),
        "user_profile": None
    }

