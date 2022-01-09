import os
from medmeapp import MedMeAppInterface


TENANT_ID = "edfbb1a3-aca2-4ee4-bbbb-9237237736c4"
ENTERPRISE_NAME = "METRO"
SUBDOMAIN = "metro"
VACCINES = [
    {
        "type": 1,
        "appointment_type_name": "COVID-19 Vaccine (Dose 1)",
        "tags": set(["12+ Year Olds", "1st Dose"]),
    },
    {
        "type": 3,
        "appointment_type_name": "COVID-19 Vaccine (Dose 2 - Moderna)",
        "tags": set(["12+ Year Olds", "Moderna", "2nd Dose"]),
    },
    {
        "type": 4,
        "appointment_type_name": "COVID-19 Vaccine (Dose 2 - Pfizer)",
        "tags": set(["12+ Year Olds", "Pfizer", "2nd Dose"]),
    },
    {
        "type": 3,
        "appointment_type_name": "COVID-19 Vaccine (Dose 3 - Moderna)",
        "tags": set(["12+ Year Olds", "Moderna", "3rd Dose"]),
    },
    {
        "type": 4,
        "appointment_type_name": "COVID-19 Vaccine (Dose 3 - Pfizer)",
        "tags": set(["12+ Year Olds", "Pfizer", "3rd Dose"]),
    },
    {
        "type": 4,
        "appointment_type_name": "COVID-19 Vaccine (Dose 1 - Pediatric)",
        "tags": set(["5-11 Year Olds", "Pfizer", "1st Dose"]),
    },
]

async def main():
    await MedMeAppInterface(TENANT_ID, ENTERPRISE_NAME, SUBDOMAIN, VACCINES).update_availabilities()
