import datetime
from datetime import datetime as dt
import json
import numpy as np
from operator import attrgetter
import statistics

from utilization.models import Patient, Provider, Specialty, Transfusion


class Product:
    def __init__(self, product_type):
        self.product_type = product_type
        self.minimum = -1
        self.median = -1
        self.maximum = -1
        self.units = []

    def to_dict(self):
        return {'product_type': self.product_type, 'minimum': self.minimum, 'median': self.median,
                'maximum': self.maximum, 'units': [unit.to_dict() for unit in self.units]}


class Unit:
    def __init__(self, value, test, u_specialty, location, color, line):
        try:
            self.value = float(value)
        except ValueError:
            self.value = value
        self.test = test
        self.specialty = u_specialty
        self.location = location
        self.color = color
        self.line = line

    def to_dict(self):
        return self.__dict__


class Provider:
    def __init__(self, name, specialty):
        self.name = name
        self.specialty = specialty

        self.fibrinogen_min = -2
        self.fibrinogen_med = -2
        self.fibrinogen_max = -2
        self.hemoglobin_min = -2
        self.hemoglobin_med = -2
        self.hemoglobin_max = -2
        self.platelet_min = -2
        self.platelet_med = -2
        self.platelet_max = -2
        self.prothrombin_min = -2
        self.prothrombin_med = -2
        self.prothrombin_max = -2

        self.cryo = []
        self.rbcs = []
        self.plasma = []
        self.platelets = []

    def to_dict(self):
        return {'name': self.name, 'specialty': self.specialty,

                'num_cryo': len(self.cryo), 'num_plasma': len(self.plasma), 'num_platelets': len(self.platelets),
                'num_rbcs': len(self.rbcs),

                'fibrinogen_min': self.fibrinogen_min,
                'fibrinogen_med': self.fibrinogen_med, 'fibrinogen_max': self.fibrinogen_max,

                'hemoglobin_min': self.hemoglobin_min,
                'hemoglobin_med': self.hemoglobin_med, 'hemoglobin_max': self.hemoglobin_max,

                'platelet_min': self.platelet_min, 'platelet_med': self.platelet_med,
                'platelet_max': self.platelet_max,

                'prothrombin_min': self.prothrombin_min,
                'prothrombin_med': self.prothrombin_med, 'prothrombin_max': self.prothrombin_max,
                }


class Specialty:
    def __init__(self, name):
        self.name = name

        self.hemoglobin_min = -2
        self.hemoglobin_med = -2
        self.hemoglobin_max = -2

        self.cryo = []
        self.rbcs = []
        self.plasma = []
        self.platelets = []

    def to_dict(self):
        return {'name': self.name, 'hemoglobin_min': self.hemoglobin_min, 'hemoglobin_med': self.hemoglobin_med,
                'hemoglobin_max': self.hemoglobin_max, 'num_rbcs': len(self.rbcs), 'num_platelets': len(self.platelets)}


def meets_criteria(col, products, per_day, start_date, end_date):
    if products != "ALL" and col[7] != products:
        return False

    if per_day and per_day < col[2]:
        return False
    if '-' in col[3]:
        date = col[3].split("-")
        transfusion_date = datetime.date(int(date[0]), int(date[1]), int(date[2]))
    elif '/' in col[3]:
        date = col[3].split('/')
        transfusion_date = datetime.date(int(date[2]), int(date[0]), int(date[1]))
    if start_date and transfusion_date < start_date:
        return False
    if end_date and transfusion_date > end_date:
        return False
    return True


def get_utilization_data(filepath, products, location, specialty, per_day, start_date, end_date):
    product_dict = {}
    product_dict["RED CELLS"] = Product("RED CELLS")
    product_dict["PLATELETS"] = Product("PLATELETS")
    product_dict["PLASMA"] = Product("PLASMA")
    product_dict["CRYOPPT"] = Product("CRYOPPT")
    tests = {"RED CELLS": "Hemoglobin:", "PLATELETS": "Platelet count:", "PLASMA": "Prothrombin time:",
             "CRYOPPT": "Fibrinogen:"}

    product_data = open(filepath, "r")
    provider_dict = {}
    specialty_dict = {}
    specialties = []
    if specialty:
        specialty = specialty.upper()
        specialties = specialty.split(",")
        for i in range(len(specialties)):
            specialties[i] = specialties[i].strip()
    if start_date:
        start = start_date.split("-")
    if end_date:
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
        product = col[7].upper()

        u_specialty = col[16].replace('"', '')
        u_specialty = u_specialty.strip().upper()
        u_location = col[14].strip()
        provider_name = col[15].strip()
        if provider_name not in provider_dict:
            provider_dict[provider_name] = Provider(provider_name, u_specialty)
        provider = provider_dict[provider_name]
        if u_specialty not in specialty_dict:
            specialty_dict[u_specialty] = Specialty(u_specialty)

        # Color of the dots on chart
        color = "zblack"
        if specialty or location != "":  # use light grey if specialty/location searched for
            color = "zrgba(0, 0, 0, 0.2)"
        for element in specialties:
            if element != "" and element in u_specialty:
                color = "rgba(212,43,0, 1)"
        if location and location.upper() in col[13].upper():
            color = "rgb(0, 204, 0)"

        if meets_criteria(col, products, per_day, start_dt, end_dt):
            unit = Unit(col[9], tests[product], u_specialty, u_location, color, line.rstrip())
            product_dict[product].units.append(unit)
            if "CRYO" in product:
                provider.cryo.append(unit)
                specialty_dict[u_specialty].cryo.append(unit)
            elif "RED" in product:
                provider.rbcs.append(unit)
                specialty_dict[u_specialty].rbcs.append(unit)
            elif "PLATE" in product:
                provider.platelets.append(unit)
                specialty_dict[u_specialty].platelets.append(unit)
            elif "PLASMA" in product:
                provider.plasma.append(unit)
                specialty_dict[u_specialty].plasma.append(unit)

    # Sort so that filtered products are all at the front
    for product in product_dict.values():
        product.units = sorted(product.units, key=attrgetter('color'))
        for unit in product.units:
            unit.color = unit.color.replace('z', '')

    for provider in provider_dict.values():
        calculate_provider_stats(provider)
    for specialty in specialty_dict.values():
        calculate_provider_stats(specialty)

    overall_statistics(product_dict)
    data = {product.product_type: product.to_dict() for product in product_dict.values()}

    provider_list = provider_dict.values()
    provider_list = sorted(provider_list, key=lambda x: x.hemoglobin_med, reverse=True)
    data['providers'] = [provider.to_dict() for provider in provider_list]

    specialty_list = specialty_dict.values()
    specialty_list = sorted(specialty_list, key=lambda x: x.hemoglobin_med, reverse=True)
    data['specialties'] = [specialty.to_dict() for specialty in specialty_list]
    return data


def overall_statistics(product_dict):
    for product in product_dict.values():
        test_vals = [unit.value for unit in product.units if unit.value != 'none']
        if test_vals:
            product.minimum = np.min(test_vals)
            product.median = np.median(test_vals)
            product.maximum = np.max(test_vals)


def calculate_provider_stats(provider):
    hgb_values = [rbc.value for rbc in provider.rbcs if rbc.value != "none"]
    if hgb_values:
        provider.hemoglobin_med = np.median(hgb_values)
        provider.hemoglobin_min = np.min(hgb_values)
        provider.hemoglobin_max = np.max(hgb_values)

    plt_values = [platelet.value for platelet in provider.platelets if platelet.value != "none"]
    if plt_values:
        provider.platelet_med = np.median(plt_values)
        provider.platelet_min = np.min(plt_values)
        provider.platelet_max = np.max(plt_values)

    pro_values = [plasma.value for plasma in provider.plasma if plasma.value != "none"]
    if pro_values:
        provider.prothrombin_med = np.median(pro_values)
        provider.prothrombin_min = np.min(pro_values)
        provider.prothrombin_max = np.max(pro_values)

    fib_values = [cryo.value for cryo in provider.cryo if cryo.value != "none"]
    if fib_values:
        provider.fibrinogen_med = np.median(fib_values)
        provider.fibrinogen_min = np.min(fib_values)
        provider.fibrinogen_max = np.max(fib_values)


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
            except:
                test_time = col[12]
            location = col[14]
            provider_first, provider_last = col[15].split(',')[1], col[15].split(',')[0]
            specialty = col[16]
