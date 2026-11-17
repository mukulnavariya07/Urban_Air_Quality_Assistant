
from services.air_quality import get_coordinates, get_air_quality

city = "Jaipur"

location = get_coordinates(city)

if location:
    print("Location:", location)

    air_data = get_air_quality(
        location["latitude"],
        location["longitude"]
    )

    print("Air Quality Data:", air_data)

else:
    print("City not found.")
