"""Project entry point.

@file main.py
@brief Demonstrates use of the iNaturalist client package.
"""

from inaturalist_client import InaturalistClient


def main():
    """Fetch OSA Conservation observations and print a short summary."""
    inaturalist_client = InaturalistClient()
    observation_response = inaturalist_client.get_osa_observations(output_file_name="osa_observations.json")
    print(f"Fetched {len(observation_response['results'])} observations")


if __name__ == "__main__":
    main()
