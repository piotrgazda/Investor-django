
from django.urls import path
from stocks import crudviews, views 
urlpatterns = [
    path('', views.homepage, name='home'),
    path('refresh/', views.refresh_data, name='refresh'),
    path('company/<company>/', views.company_stock_summary),
    path('create/company/', crudviews.CompanyCreateView.as_view()),
    path('create/follow/', crudviews.FollowedCompanyCreateView.as_view()),
    path('create/investment/', crudviews.StockInvestmentCreateView.as_view()),
    path('financials/<company>/', views.financials),
    # rest views
    path('delete/followed', crudviews.delete_followed_company),
]
