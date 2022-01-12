import logging
from typing import List
import aiohttp
import datetime

from vaccine_types import VaccineType

class VHC:
    BASE_URL = 'vax-availability-api-staging.azurewebsites.net'
    API_KEY = 'Bearer'
    VHC_ORG = 0
    VACCINES = {
        3: 'Moderna',
        4: 'Pfizer',
        5: 'AstraZeneca'
    }

    def __init__(self, base_url, api_key, org_id, session):
        self.BASE_URL = base_url
        self.API_KEY = f'Bearer {api_key}'
        self.VHC_ORG = org_id
        self.session = session
        logging.debug({
            'BASE_URL': self.BASE_URL,
            'VHC_ORG': self.VHC_ORG
        })

    def request_path(self, path):
        return f'https://{self.BASE_URL}/api/v1/{path}'

    async def add_availability(self, num_available: int, num_total: int, vaccine_type: VaccineType, location, external_key: str):
        vaccine_name = self.VACCINES.get(vaccine_type.value, 'Unknown')
        va = {
                'numberAvailable': num_available,
                'numberTotal': num_total,
                'vaccine': vaccine_type.value,
                'inputType': 1,
                'tags': '',
                'organization': self.VHC_ORG,
                'line1': location.get('line1'),
                'city': location.get('city'),
                'province': location.get('province'),
                'postcode': ''.join(location.get('postcode').split()),
                'name': location.get('name'),
                'phone': location.get('phone'),
                'active': 1,
                'url': location.get('url'),
                'tagsL': '',
                'tagsA': ','.join(location['tags']) if 'tags' in location else vaccine_name,
                'externalKey': external_key,
                'date': f'{datetime.datetime.utcnow().date()}T00:00:00+00:00'
            }
        
        response = await self.session.post(
            url=self.request_path(f'vaccine-availability/locations/key/{external_key}'),
            json=va,
            headers={ 'Authorization': self.API_KEY }
        )

        if response.status != 200:
            logging.error(f'VHC API Error - {response.status}')
            logging.error(await response.text())
        else:
            if num_available > 0 :
                logging.info(f'Available   - {vaccine_name: <11} - {location["name"]}')
            else:
                logging.info(f'Unavailable - {vaccine_name: <11} - {location["name"]}')

    async def __get_timeslots(self, vaccine_availability_id: str) -> List:
        response = await self.session.get(
            url=self.request_path(f'vaccine-availability/{vaccine_availability_id}/timeslots'),
            headers={ 'Authorization': self.API_KEY }
        )
        if response.status == 200:
            body = await response.json()
            logging.info(f'Retrieved timeslots for {vaccine_availability_id}')
            return body
        else:
            return []
    
    async def __delete_timeslots(self, vaccine_availability_id: str, timeslots: List) -> None:
        for timeslot in timeslots:
            timeslot_id = timeslot['id']
            response = await self.session.delete(
                url=self.request_path(f'vaccine-availability/{vaccine_availability_id}/timeslots/{timeslot_id}'),
                headers={ 'Authorization': self.API_KEY }
            )
            if response.status == 200:
                logging.info(f'Deleted timeslot {timeslot_id}')

    async def add_timeslots(self, vaccine_availability_id: str, times: List) -> None:
        # Get list of existing timeslots
        timeslots = await self.__get_timeslots(vaccine_availability_id)
        # Delete existing timeslots
        await self.__delete_timeslots(vaccine_availability_id, timeslots)
        # Add timeslots
        for time in times:
            response = await self.session.post(
                url=self.request_path(f'vaccine-availability/{vaccine_availability_id}/timeslots'),
                headers={ 'Authorization': self.API_KEY },
                json = { 'time': time }
            )

            if response.status == 200:
                logging.info(f'Added timeslot {time}')

    async def notify_discord(self, title, availabilities, discord_url):
        if not discord_url or len(availabilities) == 0:
            return

        logging.info(f'Notifying Discord with {len(availabilities)} availabilities')
        fields = []
        for availability in availabilities:
            fields.append({
                "name": availability['name'],
                "value": f"<{availability['url']}>"
            })
        discord = {
            "username": "Pharmacy Availability",
            "embeds": [
                {
                    "title": title,
                    "fields": fields
                }
            ]
        }

        response = await self.session.post(
            url=discord_url, 
            json=discord
        )
