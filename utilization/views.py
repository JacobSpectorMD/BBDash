from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import datetime, os
from datetime import timedelta
from utilization.models import *
from utilization.forms import FileUploadForm
from utilization.utilization_calculator import get_utilization_data, process_file


def utilization(request):
    return render(request, 'utilization.html')


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
    try:
        filepath = request.session['filepath']
        json_string = get_utilization_data(filepath, products, location, specialty, per_day,
                                           start_date, end_date)
        return JsonResponse(json_string, safe=False)
    except:
        return JsonResponse("Please upload your deidentified trial output file")


def file_upload(request):
    form = FileUploadForm(request.POST, request.FILES)
    if form.is_valid():
        newdoc = Document(file=request.FILES['file'])
        newdoc.save()
        filepath = newdoc.file.path
        # process_file(filepath)
        request.session['filepath'] = filepath
        for uploaded_file in os.listdir(os.path.dirname(filepath)):
            upload_time = datetime.datetime.fromtimestamp(os.path.getmtime('media/'+uploaded_file))
            age = datetime.datetime.now() - upload_time
            if age/timedelta(hours=1) > 1:
                os.remove('media/'+uploaded_file)
        return HttpResponse('File upload succeeded.')
    return HttpResponse("File upload not valid.")

