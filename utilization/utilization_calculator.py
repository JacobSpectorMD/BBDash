import json, datetime, statistics
import numpy as np
from operator import attrgetter
from utilization.models import Patient, Provider, Specialty, Transfusion
from datetime import datetime as dt

RBC_values = []
platelet_values = []
plasma_values = []
cryo_values = []


class Unit:
    def __init__(self, value, test, specialty, location, color, line, values_list):
        self.value = value
        self.color = color
        self.test = test
        self.location = location
        self.specialty = specialty
        self.line = line
        values_list.append(value)


def meets_criteria(col, products, per_day, start_date, end_date):
    if products != "ALL" and col[7] != products:
        return False

    if per_day != "" and per_day < col[2]:
        return False
    print(col)
    if '-' in col[3]:
        date = col[3].split("-")
    elif '/' in col[3]:
        date = col[3].split('/')
        print(date)
    transfusion_date = datetime.date(int(date[2]), int(date[0]), int(date[1]))
    if start_date and transfusion_date < start_date:
        return False
    if end_date and transfusion_date > end_date:
        return False
    return True


def get_utilization_data(filepath, products, location, specialty, per_day, start_date, end_date):
    product_data = open(filepath, "r")
    RBCs, platelets, plasma, cryo = [], [], [], []
    specialty = specialty.upper()
    specialties = specialty.split(",")
    for i in range(len(specialties)):
        specialties[i] = specialties[i].strip()
    start = start_date.split("-")
    end = end_date.split("-")
    try:
        start_dt = datetime.date(int(start[0]), int(start[1]), int(start[2]))
        end_dt = datetime.date(int(end[0]), int(end[1]), int(end[2]))
    except:
        start_dt = False
        end_dt = False
    
    for line in product_data:
        col = line.split("\t")
        if col[0].upper() == 'MRN':
            continue
        product = col[7]
        u_specialty = col[15].replace('"', '')
        u_specialty = u_specialty.strip().upper()
        u_location = col[13].strip()

        # Color of the dots on chart
        color = "zblack"
        if specialty != "" or location != "":  # use light grey if specialty/location searched for
            color = "zrgba(0, 0, 0, 0.2)"
        for element in specialties:
            if element != "" and element in u_specialty:
                color = "rgba(212,43,0, 1)"
        if location !="" and location.upper() in col[13].upper():
            color ="rgb(0, 204, 0)"

        if meets_criteria(col, products, per_day, start_dt, end_dt):
            try:
                if product == "RBC":
                    RBCs.append(Unit(float(col[9]), "Hemoglobin:", u_specialty, u_location, color, line.rstrip(), RBC_values))
                elif product == "PLATELET":
                    platelets.append(Unit(float(col[9]), "Platelet count:", u_specialty, u_location, color, line.rstrip(), platelet_values))
                elif product == "PLASMA":
                    plasma.append(Unit(float(col[9]), "Prothrombin time:", u_specialty, u_location, color, line.rstrip(), plasma_values))
                elif product == "CRYOPRECIPITATE":
                    cryo.append(Unit(float(col[9]), "Fibrinogen:", u_specialty, u_location, color, line.rstrip(), cryo_values))
            except:
                pass
    
    RBCs = sorted(RBCs, key=attrgetter('color'))
    platelets = sorted(platelets, key=attrgetter('color'))
    plasma = sorted(plasma, key=attrgetter('color'))
    cryo = sorted(cryo, key=attrgetter('color'))

    product_lists = {"RBCs":[RBCs, RBC_values], "platelets":[platelets, platelet_values], "plasma":[plasma,plasma_values],
                     "cryo":[cryo, cryo_values]}
    for key, list in product_lists.items():
        for unit in list[0]:
            unit.color = unit.color.replace("z", "")

    json_string ='{'
    for key, list in product_lists.items():
        product_median = np.median(list[1])
        product_min = np.min(list[1])
        product_average = np.mean(list[1])
        product_max = np.max(list[1])
        json_string += '"'+key+'":{"median":"'+str(product_median)+'","min":"'+str(product_min)+'", \
                       "mean":"'+str(product_average)+'","max":"'+str(product_max)+'", "units":['
        for i in range(len(list[0])):
            json_string+=json.dumps(list[0][i].__dict__)
            if i < len(list[0])-1: json_string+=','
        json_string += ']}'
        if key != "cryo":
            json_string += ','
    json_string += '}'
    product_data.close()
    return(json_string)


def process_file(filepath):
    with open(filepath, 'r') as infile:
        infile.readline()
        for line in infile:
            col = line.split('\t')
            mrn = int(col[0])
            pt_name = col[1]
            units_on_day = col[2]
            date = [int(x) for x in col[3].split('/')]
            time = [int(x) for x in col[4].split(':')]
            issue_time = dt(date[2], date[0], date[1], time[0], time[1], time[2])
            din = col[5]
            num_units = int(col[6])
            product = col[7]
            test_result = col[9]
            test_type = col[10]
            test_accession = col[11]
            try:
                split = col[12].split(' ')
                date = [int(x) for x in split[0].split('/')]
                time = [int(x) for x in split[1].split(':')]
                test_time = dt(date[2], date[0], date[1], time[0], time[1])
                print(test_time)
            except:
                test_time = col[12]
            location = col[14]
            provider_first, provider_last = col[15].split(',')[1], col[15].split(',')[0]
            specialty = col[16]
