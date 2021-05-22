from dataclasses import dataclass

from geopy import distance
from typing import Tuple, List, Optional

GREEN_LUAS = 'GREEN_LUAS'
RED_LUAS = 'RED_LUAS'


@dataclass
class PublicTransportStation:
    name: str
    coords: Tuple[float, float]
    line: str


GREEN_LUAS_STATIONS: List[PublicTransportStation] = [
    PublicTransportStation('Brides Glen', (53.2424906, -6.143736), GREEN_LUAS),
    PublicTransportStation('Cherrywood', (53.2450575, -6.145171), GREEN_LUAS),
    PublicTransportStation('Laughanstown', (53.2512891, -6.1637364), GREEN_LUAS),
    PublicTransportStation('Carrickmines', (53.2538689, -6.1721643), GREEN_LUAS),
    PublicTransportStation('Ballyogan Wood', (53.2549603, -6.1825975), GREEN_LUAS),
    PublicTransportStation('Leopardstown Valley', (53.2578556, -6.1991065), GREEN_LUAS),
    PublicTransportStation('Glencairn', (53.2646374, -6.2088009), GREEN_LUAS),
    PublicTransportStation('Central Park', (53.2687583, -6.2035692), GREEN_LUAS),
    PublicTransportStation('Sandyford', (53.2770891, -6.2025893), GREEN_LUAS),
    PublicTransportStation('Stillorgan', (53.2778283, -6.2117258), GREEN_LUAS),
    PublicTransportStation('Kilmacud', (53.2822995, -6.2242847), GREEN_LUAS),
    PublicTransportStation('Balally', (53.2858598, -6.2364818), GREEN_LUAS),
    PublicTransportStation('Dundrum', (53.2919433, -6.2470054), GREEN_LUAS),
    PublicTransportStation('Windy Arbour', (53.3011346, -6.2506238), GREEN_LUAS),
    PublicTransportStation('Milltown', (53.3089816, -6.2502017), GREEN_LUAS),
    PublicTransportStation('Cowper', (53.3147375, -6.2517094), GREEN_LUAS),
    PublicTransportStation('Beechwood', (53.3199253, -6.2534432), GREEN_LUAS),
    PublicTransportStation('Ranelagh', (53.3259769, -6.2547096), GREEN_LUAS),
    PublicTransportStation('Charlemont', (53.3300109, -6.2578607), GREEN_LUAS),
    PublicTransportStation('Harcourt', (53.3329371, -6.2602579), GREEN_LUAS),
    PublicTransportStation('St.Stephens Green', (53.3379696, -6.259504), GREEN_LUAS),
    PublicTransportStation('Dawson', (53.3392479, -6.2585844), GREEN_LUAS),
    PublicTransportStation('Trinity', (53.3437577, -6.2582376), GREEN_LUAS),
    PublicTransportStation('Marlborough', (53.3467189, -6.2578607), GREEN_LUAS),
    PublicTransportStation('Parnell', (53.3513448, -6.2586447), GREEN_LUAS),
    PublicTransportStation('Westmoreland', (53.346278, -6.2591104), GREEN_LUAS),
    PublicTransportStation('OConnell - GPO', (53.3489277, -6.2602649), GREEN_LUAS),
    PublicTransportStation('OConnell Upper', (53.3509653, -6.2610579), GREEN_LUAS),
    PublicTransportStation('Dominick', (53.3512505, -6.2649234), GREEN_LUAS),
    PublicTransportStation('Broadstone', (53.3534611, -6.2709448), GREEN_LUAS),
    PublicTransportStation('Grangegorman', (53.3556262, -6.2761222), GREEN_LUAS),
    PublicTransportStation('Phibsborough', (53.3591863, -6.2770985), GREEN_LUAS),
    PublicTransportStation('Cabra Luas', (53.363316, -6.2798666), GREEN_LUAS),
    PublicTransportStation('Broombridge', (53.3722381, -6.299876), GREEN_LUAS),
]

RED_LUAS_STATIONS: List[PublicTransportStation] = [
    PublicTransportStation('Saggart', (53.2848375, -6.4364769), RED_LUAS),
    PublicTransportStation('Fortunestown', (53.2847141, -6.4256355), RED_LUAS),
    PublicTransportStation('Citywest Campus', (53.2869318, -6.4232664), RED_LUAS),
    PublicTransportStation('Cheeverstown', (53.2902861, -6.4129345), RED_LUAS),
    PublicTransportStation('Fettercairn', (53.2931207, -6.3982897), RED_LUAS),
    PublicTransportStation('Tallaght', (53.2869703, -6.3756625), RED_LUAS),
    PublicTransportStation('Tallaght Hospital', (53.2869703, -6.3756625), RED_LUAS),
    PublicTransportStation('Cookstown', (53.2946085, -6.3837199), RED_LUAS),
    PublicTransportStation('Belgard', (53.297571, -6.3799004), RED_LUAS),
    PublicTransportStation('Kingswood', (53.3032775, -6.3690536), RED_LUAS),
    PublicTransportStation('Red Cow', (53.3141305, -6.3681845), RED_LUAS),
    PublicTransportStation('Kylemore', (53.3254869, -6.353132), RED_LUAS),
    PublicTransportStation('Bluebell', (53.3296327, -6.3336162), RED_LUAS),
    PublicTransportStation('Blackhorse', (53.3350338, -6.3293032), RED_LUAS),
    PublicTransportStation('Drimnagh', (53.3355463, -6.3220506), RED_LUAS),
    PublicTransportStation('Goldenbridge', (53.3359948, -6.313961), RED_LUAS),
    PublicTransportStation('Suir Road', (53.3359948, -6.313961), RED_LUAS),
    PublicTransportStation('Rialto', (53.3372312, -6.3018052), RED_LUAS),
    PublicTransportStation('Fatima', (53.3375643, -6.2974279), RED_LUAS),
    PublicTransportStation('James', (53.3408313, -6.297342), RED_LUAS),
    PublicTransportStation('Heuston', (53.344681, -6.2942629), RED_LUAS),
    PublicTransportStation('Museum', (53.3469227, -6.2894242), RED_LUAS),
    PublicTransportStation('Smithfield', (53.3460773, -6.2828474), RED_LUAS),
    PublicTransportStation('Four Courts', (53.3461349, -6.2767749), RED_LUAS),
    PublicTransportStation('Jervis', (53.3465064, -6.2721722), RED_LUAS),
    PublicTransportStation('Abbey Street', (53.3484022, -6.2629454), RED_LUAS),
    PublicTransportStation('Busaras', (53.349523, -6.257581), RED_LUAS),
    PublicTransportStation('Connolly', (53.3496831, -6.2545769), RED_LUAS),
    PublicTransportStation('Georges Dock', (53.3496703, -6.2545233), RED_LUAS),
    PublicTransportStation('Mayor Square', (53.3496703, -6.2473886), RED_LUAS),
    PublicTransportStation('Spencer Dock', (53.349555, -6.2389343), RED_LUAS),
    PublicTransportStation('The Point', (53.3490747, -6.2328617), RED_LUAS),
]


class PublicTransport:

    @staticmethod
    def get_closest_green_luas(coords: Optional[str]) -> Tuple[PublicTransportStation, int]:

        return PublicTransport._get_closest_station(coords, GREEN_LUAS_STATIONS)

    @staticmethod
    def get_closest_red_luas(coords: Optional[str]) -> Tuple[PublicTransportStation, int]:

        return PublicTransport._get_closest_station(coords, RED_LUAS_STATIONS)

    @staticmethod
    def _get_closest_station(coords: Optional[str], stations: List[PublicTransportStation]) \
            -> Tuple[PublicTransportStation, int]:
        default_result = stations[0], -1

        if not coords:
            return default_result

        split_coords = coords.split(",")
        if len(split_coords) != 2:
            print(f"Could not correctly parse the coords: '{coords}'")
            return default_result

        parsed_cords = (float(split_coords[0]), float(split_coords[1]))

        closest_station: PublicTransportStation = stations[0]
        closest_station_distance = PublicTransport._get_distance_to_station(closest_station, parsed_cords)

        for station in stations:
            distance_to_station = PublicTransport._get_distance_to_station(station, parsed_cords)
            if distance_to_station < closest_station_distance:
                closest_station_distance = distance_to_station
                closest_station = station

        return closest_station, closest_station_distance

    @staticmethod
    def _get_distance_to_station(station: PublicTransportStation, coords: Tuple[float, float]) -> int:
        return int(distance.distance(coords, station.coords).m)
