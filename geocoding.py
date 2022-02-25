import geopy
from geopy.adapters import AioHTTPAdapter
import asyncio
import aiohttp
import json

delimiters = [";", ".", ","]

description_pattern = \
"""
Место: {place}
{latitude_desc}
{longitude_desc}
"""
# http://localhost:8080/search?format=jsonv2&q=Monako&limit=1

class Location:
    latitude = 0
    longitude = 0


async def search_coordinates(place: str, url="http://localhost:8080/search"):
    params = {
        "format": "jsonv2",
        "q": place,
        "limit": 1
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            geo_data = await response.json()
            location = Location()
            location


async def get_place_coordinates(place: str):
    async with geopy.Nominatim(user_agent="AllHomeworkBot",
                               domain="localhost:8080",
                               adapter_factory=AioHTTPAdapter) as geolocator:
        location = await geolocator.geocode(place)
        if int(location.latitude) > 0:
            latitude_description = f"Северная широта ↑: {abs(int(location.latitude))}°"
        else:
            latitude_description = f"Южная широта ↓: {abs(int(location.latitude))}°"
        if int(location.longitude) > 0:
            longitude_description = f"Восточная долгота →: {abs(int(location.longitude))}°"
        else:
            longitude_description = f"Западная долгота ←: {abs(int(location.longitude))}°"
        await asyncio.sleep(0.2)
        return description_pattern.format(
            place=place,
            latitude_desc=latitude_description,
            longitude_desc=longitude_description
        )


def filter_spaces(item: str):
    item = item.split()
    return " ".join(item)


async def get_coords(text: str):
    places = ()
    for item in delimiters:
        cities = places.split(item)
    for item in places:
        desc = await get_place_coordinates(item)
        print(desc)
