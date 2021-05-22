from web_scraper.public_transport import PublicTransport, GREEN_LUAS_STATIONS, RED_LUAS_STATIONS


def test_get_closest_green_luas_should_return_the_closest_station():
    coords = "53.244746, -6.144861"

    result = PublicTransport.get_closest_green_luas(coords)

    assert result[0] == GREEN_LUAS_STATIONS[1]
    assert result[1] == 40


def test_get_closest_green_luas_should_return_a_default_for_invalid_coords():
    coords = None

    result = PublicTransport.get_closest_green_luas(coords)

    assert result[0] == GREEN_LUAS_STATIONS[0]
    assert result[1] == -1


def test_get_closest_red_luas_should_return_the_closest_station():
    coords = "53.284235, -6.428219"

    result = PublicTransport.get_closest_red_luas(coords)

    assert result[0] == RED_LUAS_STATIONS[1]
    assert result[1] == 180


def test_get_closest_red_luas_should_return_a_default_for_invalid_coords():
    coords = None

    result = PublicTransport.get_closest_red_luas(coords)

    assert result[0] == RED_LUAS_STATIONS[0]
    assert result[1] == -1
