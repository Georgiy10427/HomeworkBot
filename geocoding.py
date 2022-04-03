import asyncio
import aiohttp
import aioredis
from functools import lru_cache

nominatim_url = "https://nominatim.openstreetmap.org/search"
# nominatim_url = "http://localhost:8080/search"
delimiters = [";", ".", ","]

description_pattern = \
"""
Место: {place}
{latitude_desc}
{longitude_desc}
"""


class Location:
    latitude = 0
    longitude = 0


async def geocode(place: str, url=nominatim_url):
    params = {
        "format": "jsonv2",
        "q": place,
        "limit": 1
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            geo_data = await response.json()
            location = Location()
            location.latitude = float(geo_data[0]["lat"])
            location.longitude = float(geo_data[0]["lon"])
            return location


@lru_cache(maxsize=50)
async def get_place_coordinates(place: str):
    location = await geocode(place)
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
    places = text.split(";")
    for item in places:
        desc = await get_place_coordinates(item)
        print(desc)
