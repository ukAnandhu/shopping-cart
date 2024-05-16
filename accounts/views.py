from django.http import HttpResponse
from django.shortcuts import redirect, render
import requests

from cart.models import Cart, CartItem
from cart.views import _cart_id
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required

#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

def register(req):
    if req.method == 'POST':
        form = RegistrationForm(req.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phn']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
           
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.phone_number=phone_number
            user.save()

            current_site = get_current_site(req)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_varification_mail.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), #user primary encode
                'token':default_token_generator.make_token(user), #generate token
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            
            send_email.send()
            # messages.success(req,'We have send you a verification mail to you email.Please verify it')

            return redirect('/accounts/login/?command=verification&email='+email)
            # return HttpResponse("Registration successful!")  # Return a success message
    else:
        form = RegistrationForm()

    return render(req, 'accounts/register.html', {'form': form})
def login(req):
    if req.method == 'POST':
        email = req.POST['email']
        password  = req.POST['password']

        user = auth.authenticate(email=email,password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(req))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    product_variation = []
                    #product variation by cart id
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                        #get cart item from user
                        cart_item = CartItem.objects.filter(user=user)
                        ex_var_list = []
                        id = []
                        for item in cart_item:
                            existing_variation = item.variations.all()
                            ex_var_list.append(list(existing_variation))
                            id.append(item.id)
                        for pv in product_variation:
                            if pv in ex_var_list:
                                index = ex_var_list.index(pv)
                                item_id = id[index]
                                item = CartItem.objects.get(id=item_id)
                                item.quantity += 1
                                item.user = user
                                item.save()
                            else:
                                cart_item = CartItem.objects.filter(car=cart)
                                for item in cart_item:
                                    item.user = user
                                    item.save() 
            except:
                pass
            auth.login(req,user)  
            messages.success(req,'You are logged in!')
            url = req.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                print(query)
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return  redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(req,'Inavlid Login Credentials')
            return redirect('login')

    return render(req,'accounts/login.html')

@login_required(login_url= 'login')
def logout(req):
    auth.logout(req)
    messages.success(req,"You are logged out")
    return redirect('login') 


def activate(req,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(req,'Congratulations your activated')
        return redirect('login')
    else:
        messages.error(req,'Inavlid activation link')
        return redirect('register')

#dashboard
@login_required(login_url = 'login')
def dashboard(req):
    return render(req,'accounts/dashboard.html')



def forgotpassword(req):
    if req.method == 'POST':
        email = req.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            #Reset pwd
            current_site = get_current_site(req)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), #user primary encode
                'token':default_token_generator.make_token(user), #generate token
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(req,'Password email hase been sent to your email adddress!')

            return redirect('login')
        else:
            messages.error(req,'Account does not exist!')
            return redirect('forgotpassword')
    return render(req,'accounts/forgotpassword.html')


def resetpassword_validate(req,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        req.session['uid'] = uid
        messages.success(req,'reset your password')
        return redirect('resetpassword')
    else:
        messages.error(req,'This link has been expired')
        return redirect('login')
    
def resetpassword(req):
    if req.method == 'POST':
        password = req.POST['password']
        confirm_password  =req.POST['confirm_password']
        if password == confirm_password:
            uid = req.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(req,'Password reset successfull')
            return redirect('login')
        else:
            messages.error(req,"Paswword do not match!")
            return redirect('resetpassword')
    else:
        return render(req,'accounts/resetpassword.html')