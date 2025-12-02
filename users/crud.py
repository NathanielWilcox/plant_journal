from django.contrib.auth import get_user_model

def create_user(**kwargs):
    user = get_user_model().objects.create_user(**kwargs)
    return user

def update_user(user, **kwargs):
    for attr, value in kwargs.items():
        setattr(user, attr, value)
    user.save()
    return user

def delete_user(user):
    user.delete()