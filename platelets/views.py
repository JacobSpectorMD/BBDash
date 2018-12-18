from django.shortcuts import render


def platelets(request):
    return render(request, 'platelets.html')
