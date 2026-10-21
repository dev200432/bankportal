from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Account, Transaction
import random

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # ऑटोमैटिक 10-अंकों का बैंक अकाउंट नंबर जेनरेट करना
            acc_num = str(random.randint(1000000000, 9999999999))
            Account.objects.create(user=user, account_number=acc_num, balance=1000.00)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    account = request.user.account
    transactions = account.transactions.order_by('-timestamp')[:5]
    return render(request, 'dashboard.html', {'account': account, 'transactions': transactions})

from decimal import Decimal # <-- यह ऊपर इम्पोर्ट करना ज़रूरी है

@login_required
def deposit_view(request):
    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        if amount_str:
            amount = Decimal(amount_str) # Decimal में कन्वर्ट करें
            if amount > 0:
                account = request.user.account
                account.balance += amount
                account.save()
                Transaction.objects.create(account=account, transaction_type='DEPOSIT', amount=amount, description='Self Deposit')
                messages.success(request, f'Successfully deposited ₹{amount}')
                return redirect('dashboard')
    return render(request, 'deposit.html')

@login_required
def withdraw_view(request):
    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        if amount_str:
            amount = Decimal(amount_str) # Decimal में कन्वर्ट करें
            account = request.user.account
            if 0 < amount <= account.balance:
                account.balance -= amount
                account.save()
                Transaction.objects.create(account=account, transaction_type='WITHDRAW', amount=amount, description='Self Withdrawal')
                messages.success(request, f'Successfully withdrew ₹{amount}')
                return redirect('dashboard')
            else:
                messages.error(request, 'Insufficient balance!')
    return render(request, 'withdraw.html')