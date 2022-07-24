from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ValidationError
from django.http import Http404 
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView
from rest_framework.response import Response
from rest_framework.decorators import api_view

import pandas as pd

from stocks.forms import InvestmentForm
from stocks.models import *
from stocks.renders import render_table
from stocks.df import  add_delete_button




@method_decorator(login_required, name='dispatch')
class CompanyCreateView(CreateView):
    template_name = 'stocks/create-form.html'

    model = Company
    fields = ['name', 'abbreviation']
    success_url = reverse_lazy('home')

    def get(self, request):
        companies = pd.DataFrame(Company.objects.active().values('name', 'abbreviation')).rename(
            columns={'name': 'Name', 'abbreviation': 'Abbreviation'})
        return render(request, template_name=self.template_name, context={'form': self.get_form_class()(), 'items': render_table(df=companies, title='Companies')})


@method_decorator(login_required, name='dispatch')
class FollowedCompanyCreateView(CreateView):
    template_name = 'stocks/create-form.html'

    model = UserFollowedCompanies
    fields = ['company']
    delete_url = '/delete/followed'

    def get(self, request):
        user_followed = pd.DataFrame(UserFollowedCompanies.objects.user_followed_companies(
            request.user).order_by('company__abbreviation').values('company__abbreviation')).rename(columns={'company__abbreviation': 'Company'})
        user_followed = add_delete_button(user_followed, 'Unfollow')
        return render(request, template_name=self.template_name, context={'form': self.get_form_class()(),
                                                                          'items': render_table(df=user_followed, title='Followed companies'),
                                                                          'delete_url': self.delete_url})

    def post(self, request):
        company = request.POST.get('company', None)
        if not company or not Company.objects.filter(pk=company):
            return Http404('Not exist')

        new_follow = UserFollowedCompanies(
            user=request.user, company_id=company)
        new_follow.save()
        return redirect('home')


@method_decorator(login_required, name='dispatch')
class StockInvestmentCreateView(CreateView):
    template_name = 'stocks/create-form.html'
    form_class = InvestmentForm
    model = UserStockTransactions
    success_url = reverse_lazy('home')
    delete_url = ''

    def get(self, request):
        user_investments = pd.DataFrame(UserStockTransactions.objects.stocks_of_user(
            request.user).order_by('-date').values('company__abbreviation', 'quantity', 'buy', 'price', 'date')).rename(columns={'company__abbreviation': 'Company', 'quantity': 'Quantity', 'price': 'Price', 'date': 'Date', 'buy': 'Type'})
        user_investments['Type'] = user_investments['Type'].astype(str)
        user_investments.loc[user_investments['Type']
                             == "True", 'Type'] = 'Buy'
        user_investments.loc[user_investments['Type']
                             == "False", 'Type'] = 'Sell'

        return render(request, template_name=self.template_name, context={'form': self.get_form_class()(), 'items': render_table(df=user_investments, title='Followed companies')})

    def post(self, request):

        form = InvestmentForm(request.POST)
        if form.is_valid():
            new_transaction = UserStockTransactions(
                user=request.user, **form.cleaned_data)
            new_transaction.save()
        return redirect('home')

@api_view(["POST"])
def delete_followed_company(request):
    company_abbreviation = request.POST.get("company")
    if not company_abbreviation:
        raise ValidationError('Company abbreviation was not sent')
    company = UserFollowedCompanies.objects.user_followed_company_by_abbreviation(
        request.user, company_abbreviation)
    if not company:
        raise ObjectDoesNotExist('Company to delete does not exist in db')
    response = company.delete()
    return Response()