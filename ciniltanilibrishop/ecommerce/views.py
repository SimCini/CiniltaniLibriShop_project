from django.shortcuts import render


def chi_sono(request):
    return render(request, 'chi_sono.html')