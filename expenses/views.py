from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Transaction, Category
from .forms import TransactionForm
from django.db.models import Sum
from django.contrib import messages

def home(request):
    return render(request, 'home.html')

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
    @login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    
    # Basic filter by type
    transaction_type = request.GET.get('type')
    if transaction_type in ['income', 'expense']:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    context = {
        'transactions': transactions,
        'total_income': transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_expense': transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    return render(request, 'transaction_list.html', context)
@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'category_list.html', {'categories': categories})
