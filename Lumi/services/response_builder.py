def build_description_response(place):

    return {
        "speech": f"{place['name']} es {place['description']}",

        "avatar": {
            "animation": "talk"
        },

        "map": {
            "latitude": place["latitude"],
            "longitude": place["longitude"]
        },

        "image": place["image"],

        "place": place
    }


def build_schedule_response(place):

    return {

        "speech": (
            f"El horario de {place['name']} es "
            f"{place['schedule']}."
        ),

        "avatar": {
            "animation": "talk"
        },

        "map": {
            "latitude": place["latitude"],
            "longitude": place["longitude"]
        },

        "image": place["image"],

        "place": place
    }


def build_location_response(place):

    return {

        "speech": (
            f"{place['name']} está ubicado en las coordenadas "
            f"{place['latitude']}, {place['longitude']}."
        ),

        "avatar": {
            "animation": "talk"
        },

        "map": {
            "latitude": place["latitude"],
            "longitude": place["longitude"]
        },

        "image": place["image"],

        "place": place
    }


def build_category_response(category, places):

    if not places:

        return {
            "speech": f"No encontré lugares de la categoría {category}.",
            "places": []
        }

    names = ", ".join(place["name"] for place in places)

    return {

        "speech": f"Encontré {len(places)} lugar(es): {names}.",

        "avatar": {
            "animation": "talk"
        },

        "places": places
    }


def build_recommendation_response(place):

    return {

        "speech": (
            f"Te recomiendo visitar {place['name']}. "
            f"{place['description']}"
        ),

        "avatar": {
            "animation": "talk"
        },

        "map": {
            "latitude": place["latitude"],
            "longitude": place["longitude"]
        },

        "image": place["image"],

        "place": place
    }