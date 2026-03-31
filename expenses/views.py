from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
import csv

from .models import Transaction, Category
from .forms import TransactionForm

# Home
def home(request):
    return render(request, 'home.html')

# Dashboard
@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user)
    
    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'transactions': transactions.order_by('-date')[:5],
    }
    return render(request, 'dashboard.html', context)

# Add Transaction
@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, "Transaction added successfully!")
            return redirect('dashboard')
    else:
        form = TransactionForm(user=request.user)
    
    return render(request, 'add_transaction.html', {'form': form})

# Transaction List
@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    
    transaction_type = request.GET.get('type')
    if transaction_type in ['income', 'expense']:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        transactions = transactions.filter(date__range=[start_date, end_date])

    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'transaction_list.html', context)

# Edit Transaction
@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated successfully!")
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    return render(request, 'edit_transaction.html', {'form': form})

# Delete Transaction
@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, "Transaction deleted successfully!")
        return redirect('transaction_list')
    return render(request, 'delete_transaction.html', {'transaction': transaction})

# Export CSV
@login_required
def export_csv(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Category', 'Description', 'Amount'])
    
    for trans in transactions:
        writer.writerow([
            trans.date,
            trans.transaction_type,
            trans.category.name,
            trans.description,
            trans.amount
        ])
    
    return response

# Auth Views
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')
