from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMessage
from .settings import EMAIL_FROM

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh), str(refresh.access_token)

def response(message, content=False, success=True, code=False, error=False, status_code=200):
    """
        Summary or Description of the Function
        Parameters:
            message (string):
            content (any):
            success (bool):
            code    (string):
            error   (dict):
            status_code (int): default 200
        Returns:
            dict : Returning response object
    """
    response = {}
    response['message'] = message
    response['success'] = success

    if not success:
        response['code'] = code
    if content or content == []:
        response['content'] = content
    if type(error) is not bool:
        response['success'] = False
        response['code'] = code
        response['error'] = error
    return Response(response,status_code)


def send_email(data):
    email = EmailMessage(
        subject = data.get('subject'),
        body = data.get('body'),
        from_email = EMAIL_FROM,
        to = [data.get('to_email'), ],
    )
    email.send()
