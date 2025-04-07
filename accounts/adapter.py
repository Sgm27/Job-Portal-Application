from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # Limit signups if needed
        return getattr(settings, 'ACCOUNT_ALLOW_SIGNUPS', True)

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        # Allow social account signup
        return getattr(settings, 'SOCIALACCOUNT_ALLOW_SIGNUPS', True)
    
    def populate_user(self, request, sociallogin, data):
        # Call the default method first
        user = super().populate_user(request, sociallogin, data)
        
        # Set default user type as job_seeker for social accounts
        user.user_type = 'job_seeker'
        
        # Try to get user's name from social account data
        if sociallogin.account.provider == 'google':
            user_data = sociallogin.account.extra_data
            if 'picture' in user_data:
                # Here you could save the profile picture but would need additional handling
                pass
        
        if sociallogin.account.provider == 'facebook':
            user_data = sociallogin.account.extra_data
            # Handle any Facebook-specific data
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # After user is saved, you can perform additional actions
        return user