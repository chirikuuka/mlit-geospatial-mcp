from utils.definitions import ApiSpec


def build_payload(*, spec: ApiSpec, args: dict) -> dict:
    """Build the internal request payload without logging coordinates."""
    payload = {
        "coordinates": [
            {
                "lat": float(args["lat"]),
                "lon": float(args["lon"]),
            }
        ],
        "target_apis": args["target_apis"],
    }

    for param in spec.allowed_params:
        if param in args:
            payload[param] = args[param]

    return payload
