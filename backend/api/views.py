from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import redirect
from requests_oauthlib import OAuth2Session


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


@api_view(["GET"])
def oura_login(request):
    oauth = OAuth2Session(settings.OURA_CLIENT_ID, redirect_uri=settings.OURA_REDIRECT_URI, scope=settings.OURA_SCOPES)
    authorization_url, state = oauth.authorization_url(settings.OURA_AUTHORIZATION_URL)
    request.session["oura_oauth_state"] = state
    return redirect(authorization_url)


@api_view(["GET"])
def oura_callback(request):
    state = request.session.get("oura_oauth_state")
    oauth = OAuth2Session(settings.OURA_CLIENT_ID, state=state, redirect_uri=settings.OURA_REDIRECT_URI)
    token = oauth.fetch_token(
        settings.OURA_TOKEN_URL,
        client_secret=settings.OURA_CLIENT_SECRET,
        authorization_response=request.build_absolute_uri(),
    )
    request.session["oura_token"] = token
    return Response({"authenticated": True})


@api_view(["GET"])
def oura_me(request):
    token = request.session.get("oura_token")
    if not token:
        return Response({"detail": "Not authenticated"}, status=401)
    client = OAuth2Session(settings.OURA_CLIENT_ID, token=token)
    # Example user info endpoint; adjust per Oura API version
    resp = client.get("https://api.ouraring.com/v2/usercollection/personal-info")
    return Response(resp.json(), status=resp.status_code)
