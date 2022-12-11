from django.shortcuts import render
from django.http import HttpResponse
from .models import *
import datetime
from django.db import connection
# Create your views here.
def home(req):

    cdata=category.objects.all().order_by('-id')[0:6]
    pdata=product.objects.all().order_by('-id')[0:6]
    numitem=addtocart.objects.all().count()

    return render(req,'user/index.html',{"data":cdata,"products":pdata,"nitem":numitem})

def about(req):
    numitem=addtocart.objects.all().count()
    return render(req,'user/about.html',{"nitem":numitem})

def contactus(request):
    status=False
    if request.method=='POST':
        Name=request.POST.get("name","")
        Mobile=request.POST.get("mobile","")
        Email=request.POST.get("email","")
        Message=request.POST.get("msg","")
        res=contact(name=Name,contact=Mobile,email=Email,message=Message)
        res.save()
        status=True
        #return HttpResponse("<script>alert('Thanks For Enquiry..');window.location.href='/user/contactus/'</script>")
    numitem=addtocart.objects.all().count()
    return render(request,'user/contactus.html',{'S':status,"nitem":numitem})

def services(req):
    numitem=addtocart.objects.all().count()
    return render(req,'user/services.html',{"nitem":numitem})

def myorder(request):
    numitem=addtocart.objects.all().count()
    userid=request.session.get('userid')
    oid=request.GET.get('oid')
    orderdata=""
    if userid:
        cursor=connection.cursor()
        cursor.execute("select o.*,p.* from user_order o,user_product p where o.pid=p.id and o.userid='"+str(userid)+"'")
        orderdata=cursor.fetchall()
        if oid:
            result=order.objects.filter(id=oid,userid=userid)
            result.delete()
            return HttpResponse("<script>alert('Your order has been Cancelled');window.location.href='/user/myorder'</script>")
    return render(request,'user/myorder.html',{"pendingorder":orderdata,"nitem":numitem})

def myprofile(request):
        numitem=addtocart.objects.all().count()
        user=request.session.get('userid')
        pdata=profile.objects.filter(email=user)
        if user:
            if request.method == 'POST':
                name = request.POST.get("name", "")
                DOB = request.POST.get("dob", "")
                Mobile = request.POST.get("mobile", "")
                Password = request.POST.get("passwd", "")
                ProfilePhoto = request.POST.get("myfile","")
                Address = request.POST.get("address", "")
                profile(email=user,name=name,dob=DOB,passwd=Password,mobile=Mobile,myfile=ProfilePhoto,address=Address).save()
                return HttpResponse("<script>alert('Your Profile updated Successfully..');window.location.href='/user/myprofile'</script>")

        return render(request,'user/myprofile.html',{"profile":pdata,"nitem":numitem})

def prod(request):
    numitem=addtocart.objects.all().count()
    cdata=category.objects.all().order_by('-id')
    x=request.GET.get('abc')

    if x is not None:
        pdata=product.objects.filter(category=x)
    else:
        pdata = product.objects.all().order_by('-id')

    return render(request,'user/products.html',{"cat":cdata,"products":pdata,"nitem":numitem})

def signup(request):
    numitem=addtocart.objects.all().count()
    status=False
    if request.method=='POST':
        name=request.POST.get("name","")
        DOB=request.POST.get("dob","")
        Mobile=request.POST.get("mobile","")
        Email=request.POST.get("email","")
        Password=request.POST.get("passwd","")
        ProfilePhoto=request.FILES['myfile']
        Address=request.POST.get("address","")
        d=profile.objects.filter(email=Email)

        if d.count()>0:
            return HttpResponse("<script>alert('You are already registered..');window.location.href='/user/signup/'</script>")
        else:
            res=profile(name=name,dob=DOB,mobile=Mobile,email=Email,passwd=Password,myfile=ProfilePhoto,address=Address)
            res.save()
            return HttpResponse("<script>alert('You are registered successfully..');window.location.href='/user/signup/'</script>")

        #return HttpResponse("<script>alert('Thanks For SignUp..');window.location.href='/user/signup/';</script>")
    return render(request,'user/signup.html',{"nitem":numitem})

def signin(request):
    numitem=addtocart.objects.all().count()
    if request.method=='POST':

        uname=request.POST.get("uname")
        passwd=request.POST.get("passwd")
        checkuser=profile.objects.filter(email=uname,passwd=passwd)
        if(checkuser):
            request.session['userid']=uname
            return HttpResponse("<script>alert('Logged In Successfully');window.location.href='/user/signin';</script>")

        else:
            return HttpResponse("<script>alert('UserID or Password is Incorrect');window.location.href='/user/signin';</script>")
    return render(request,'user/signin.html',{"nitem":numitem})

def viewdetails(request):
    numitem=addtocart.objects.all().count()
    a=request.GET.get('msg')
    data=product.objects.filter(id=a)

    return render(request,'user/viewdetails.html',{"d":data,"nitem":numitem})

def process(request):
    userid=request.session.get('userid')
    pid=request.GET.get('pid')
    btn=request.GET.get('bn')
    if userid is not None:
        if btn=='cart':
            checkcartitem=addtocart.objects.filter(pid=pid,userid=userid)
            if checkcartitem.count()==0:
                addtocart(pid=pid,userid=userid,status=True,cdate=datetime.datetime.now()).save()
                return HttpResponse("<script>alert('Your items is successfully added in cart..');window.location.href='/user/home/'</script>")
            else:
                return HttpResponse("<script>alert('This item is already in cart...');window.location.href='/user/home/'</script>")
        elif btn=='order':
            order(pid=pid,userid=userid,remarks="pending",status=True,odate=datetime.datetime.now()).save()
            return HttpResponse("<script>alert('Your order have confirmed..');window.location.href='/user/myorder/'</script>")
        
        elif btn=='orderfromcart':
            res=addtocart.objects.filter(pid=pid,userid=userid)
            res.delete()
            order(pid=pid,userid=userid,remarks="pending",status=True,odate=datetime.datetime.now()).save()
            return HttpResponse("<script>alert('Your order have confirmed..');window.location.href='/user/myorder/'</script>")
        return render(request,'user/process.html',{"alreadylogin":True})
    else:
        return HttpResponse("<script>window.location.href='/user/signin/'</script>")


def logout(request):
    del request.session['userid']
    return HttpResponse("<script>window.location.href='/user/home/'</script>")


def cart(request):
    numitem=addtocart.objects.all().count()
    if request.session.get('userid'):
        userid=request.session.get('userid')
        cursor=connection.cursor()
        cursor.execute("select c.*,p.* from user_addtocart c,user_product p where p.id=c.pid and userid='"+str(userid)+"'")
        cartdata=cursor.fetchall()
        pid=request.GET.get('pid')
        if request.GET.get('pid'):
            res=addtocart.objects.filter(id=pid,userid=userid)
            res.delete()
            return HttpResponse("<script>alert('Your product has been Remove successfully');window.location.href='/user/cart'</script>")


    return render(request,'user/cart.html',{"cart":cartdata,"nitem":numitem})


