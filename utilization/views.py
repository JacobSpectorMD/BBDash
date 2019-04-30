import datetime
from datetime import timedelta
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from utilization.models import Document
from utilization.forms import FileUploadForm
from utilization.utilization_calculator import get_utilization_data, process_file


def units(request):
    return render(request, 'units.html', {'title': 'Units'})


def providers(request):
    return render(request, 'providers.html', {'title': 'Providers'})


def sort(request):
    template_name = "sort.html"
    return render(request, template_name)


def utilization_data(request):
    products = request.GET.get("products", None)
    location = request.GET.get("location", None)
    specialty = request.GET.get("specialty", None)
    per_day = request.GET.get("per_day", None)
    start_date = request.GET.get("start_date", None)
    end_date = request.GET.get("end_date", None)
    print(request)
    try:
        filepath = request.session['filepath']
        json_string = get_utilization_data(filepath, products, location, specialty, per_day,
                                           start_date, end_date)
        return JsonResponse(json_string, safe=False)
    except KeyError:
        return JsonResponse("Please upload your deidentified trial output file")


def file_upload(request):
    form = FileUploadForm(request.POST, request.FILES)
    if form.is_valid():
        newdoc = Document(file=request.FILES['file'])
        if 'deidentified' not in newdoc.file.name.lower():
            return HttpResponse('The file name must contain the word "deidentified" and cannot contain any patient'
                                'information')
        newdoc.save()
        filepath = newdoc.file.path
        request.session['filepath'] = filepath
        for uploaded_file in os.listdir(os.path.dirname(filepath)):
            upload_time = datetime.datetime.fromtimestamp(os.path.getmtime('media/'+uploaded_file))
            age = datetime.datetime.now() - upload_time
            if age/timedelta(hours=1) > 1:
                os.remove('media/'+uploaded_file)
        data = file_data(filepath)
        return JsonResponse(data)
    return HttpResponse("File upload not valid.")


def file_data(filepath):
    infile = open(filepath, 'r')
    infile.seek(0, 0)
    locations, providers, specialties = {}, {}, {}
    for line in infile:
        col = line.split('\t')
        if col[0] == 'MRN':
            continue
        location = col[14].replace('"', '').strip()
        provider = col[15].replace('"', '').strip()
        specialty = col[16].replace('"', '').strip()
        if location != '' and location not in locations:
            locations[location] = ''
        if provider != '' and provider not in providers:
            providers[provider] = ''
        if specialty != '' and specialty not in specialties:
            specialties[specialty] = ''

    location_list = sorted(locations.keys())
    provider_list = sorted(providers.keys())
    specialty_list = sorted(specialties.keys())
    data = {'locations': location_list, 'providers': provider_list, 'specialties': specialty_list}
    return data

