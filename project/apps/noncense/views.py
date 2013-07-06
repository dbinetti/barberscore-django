from twilio import TwilioRestException

from django.http import (
    HttpResponse,
)

from django.shortcuts import (
    render,
    redirect)

from django.contrib.auth import (
    authenticate,
    login as django_login)

from django.views.decorators.csrf import csrf_exempt

from .forms import AuthRequestForm, AuthResponseForm, AltLoginForm

from .utils import sendcode

from .models import InboundSMS


@csrf_exempt
def noncense_request(
        request,
        template_name='noncense_request.html',
        auth_request_form=AuthRequestForm):

    request_form = auth_request_form(data=request.POST or None)
    if request_form.is_valid():
        mobile = request.POST['mobile']
        try:
            nonce_return = sendcode(mobile)
        except TwilioRestException:
            return redirect('alt_login')
        request.session['nonce'] = nonce_return['nonce']
        request.session['mobile'] = nonce_return['mobile']
        request.session['count'] = 0
        return redirect('noncense_response')
    return render(request, template_name, {'request_form': request_form})


@csrf_exempt
def noncense_response(
        request,
        template_name='noncense_response.html',
        auth_response_form=AuthResponseForm):

    response_form = auth_response_form(data=request.POST or None)
    if response_form.is_valid():
        mobile = request.session['mobile']
        # strip out formatting from twilio
        mobile = mobile[-10:]
        nonce = request.session['nonce']
        code = response_form.cleaned_data['code']
        match = (str(code) == str(nonce))
        if request.session['count'] < 3:
            if match:
                user = authenticate(mobile=mobile)
                django_login(request, user)
                return redirect('home')
            else:
                request.session['count'] += 1
        else:
            request.session.flush()
            return redirect('home')
    return render(request, template_name, {'response_form': response_form})


def alt_login(request, template_name='alternate_login.html'):
    alt_login_form = AltLoginForm(data=request.POST or None)
    if alt_login_form.is_valid():
        mobile = request.POST['mobile']
        user = authenticate(mobile=mobile)
        django_login(request, user)
        return redirect('home')
    else:
        return render(request, template_name, {'alt_login_form': alt_login_form})


@csrf_exempt
def noncense_inbound(request):

    inbound = request.POST
    # inbound_test = inbound.__getitem__('baz')

    smsmessagesid = inbound.__getitem__('SmsMessageSid')
    accountsid = inbound.__getitem__('accountsid')
    body = inbound.__getitem__('body')
    fromzip = inbound.__getitem__('fromzip')
    to = inbound.__getitem__('to')
    tocity = inbound.__getitem__('tocity')
    smssid = inbound.__getitem__('smssid')
    fromstate = inbound.__getitem__('fromstate')
    tocountry = inbound.__getitem__('tocountry')
    _from = inbound.__getitem__('from')
    apiversion = inbound.__getitem__('apiversion')
    fromcity = inbound.__getitem__('fromcity')
    tozip = inbound.__getitem__('tozip')
    smsstatus = inbound.__getitem__('smsstatus')
    tostate = inbound.__getitem__('tostate')
    fromcountry = inbound.__getitem__('fromcountry')

    i = InboundSMS(
        inbound_raw=inbound_test,
        smsmessagesid=smsmessagesid,
        accountsid=accountsid,
        body=body,
        fromzip=fromzip,
        to=to,
        tocity=tocity,
        smssid=smssid,
        fromstate=fromstate,
        tocountry=tocountry,
        _from=_from,
        apiversion=apiversion,
        fromcity=fromcity,
        tozip=tozip,
        smsstatus=smsstatus,
        tostate=tostate,
        fromcountry=fromcountry)
    i.save()
    response = HttpResponse("Your text has been received and will be handled ASAP.", content_type="text/plain")
    return response
