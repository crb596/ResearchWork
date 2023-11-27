from mongodb_operations import connect_to_mongodb, insert_document, close_connection
from search import scrape_airbnb_properties
from datetime import datetime
import asyncio

async def main():
    # ======== Connect to MongoDB ========
    
    # Specify the collection name
    target_collection_name = "Scrapes"

    # Connect to MongoDB with the specified collection name
    client, collection = connect_to_mongodb(target_collection_name)

    # If the connection is successful, proceed to running the scrape
    if client is not None and collection is not None:

        # Parameters for the search

        # Bounding box

        # AD zoomed out
        # ne_lat=24.650879984872507
        # ne_lng=54.6066784669988
        # sw_lat=24.319659824397448
        # sw_lng=54.29811961731616

        # AD 761 listings
        # ne_lat = 24.52743480283826
        # ne_lng = 54.442760874360545
        # sw_lat = 24.395174645771792
        # sw_lng = 54.338766248809236

        # Yas 79 listings
        # ne_lat = 24.486571934981825
        # ne_lng = 54.62279642529387
        # sw_lat = 24.478865894582416
        # sw_lng = 54.61673622632355

        # 404 listings on Yas
        # ne_lat=24.579514700894297
        # ne_lng=54.723172969581896
        # sw_lat=24.355272483471733
        # sw_lng=54.51430277281315

        # 853 in AD
        # ne_lat=24.565350226802018
        # ne_lng=54.487873100475554
        # sw_lat=24.34110288301521
        # sw_lng=54.2790216210789

        # Zoomed out UAE - 25,796 results found on 27/11/2023
        ne_lat=25.930455013571983
        ne_lng=55.57628890102066
        sw_lat=24.12934378807139
        sw_lng=53.8909376883409

        subdivide_search = True #Continue searching with a new scrape if more than 270 results are found

        await run_search(collection, ne_lat, ne_lng, sw_lat, sw_lng, subdivide_search)

        # Close the MongoDB connection
        if client is not None:
            close_connection(client)


# Function to run searches
async def run_search(collection, ne_lat, ne_lng, sw_lat, sw_lng, subdivide_search):

    # Run the search
    
    base_url = f"https://www.airbnb.ae/s/United-Arab-Emirates/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&price_filter_input_type=0&channel=EXPLORE&query=United%20Arab%20Emirates&adults=1&source=structured_search_input_header&search_type=user_map_move&ne_lat={ne_lat}&ne_lng={ne_lng}&sw_lat={sw_lat}&sw_lng={sw_lng}&search_by_map=true&place_id=ChIJvRKrsd9IXj4RpwoIwFYv0zM"
    print("Running search on")
    print(ne_lat, ne_lng, sw_lat, sw_lng)
    try:
        scrape_results, scrape_count, results_count = await scrape_airbnb_properties(base_url)
        # print("Found: ", scrape_results, scrape_count, results_count)
        # Record this scrape's results
        if scrape_count > 0:

            new_document = {
                "date": datetime.utcnow(),
                "type": "search",
                "scrape_url": base_url,
                "search_bounding_coords": [{"ne": [ne_lat,ne_lng]}, {"sw": [sw_lat,sw_lng]}],
                "results": scrape_results,
                "result_count": scrape_count,
                "status": "OK"
            }
            insert_document(collection, new_document)

    except Exception as e:
        print(f"Error: {e}")
        # Record this scrape and error
        new_document = {
            "date": datetime.utcnow(),
            "type": "search",
            "scrape_url": base_url,
            "search_bounding_coords": [{"ne": [ne_lat,ne_lng]}, {"sw": [sw_lat,sw_lng]}],
            "error": e,
            "status": "ERROR"
        }
        insert_document(collection, new_document)

    # If there were more than 270 results, and subdivide_search is true, run another search on 4 quadrants recursively
    if results_count > 270 and subdivide_search:
        # Get half way coord points
        lat_mid = (ne_lat + sw_lat) / 2
        lng_mid = (ne_lng + sw_lng) / 2
        print("Run this again as there were:", results_count, "and", scrape_count, "were written")
        await run_search(collection, ne_lat, ne_lng, lat_mid, lng_mid, subdivide_search)
        await run_search(collection, lat_mid, ne_lng, sw_lat, lng_mid, subdivide_search)
        await run_search(collection, lat_mid, lng_mid, sw_lat, sw_lng, subdivide_search)
        await run_search(collection, ne_lat, lng_mid, lat_mid, sw_lng, subdivide_search)

if __name__ == "__main__":
    asyncio.run(main())
#     # Sample data for the new document
#     new_document = {
#         "id": 123,
#         "date": datetime.utcnow(),
#         "type": "search",  # or "property"
#         "search_property_id": 456,
#         "search_bounding_coords": [{"coord1": "value1"}, {"coord2": "value2"}],
#         "results": [
#             {"page": 1, "properties": [{"prop1": "value1"}, {"prop2": "value2"}]},
#             {"page": 2, "properties": [{"prop3": "value3"}, {"prop4": "value4"}]}
#         ]
#     }

#     # Specify the collection name
#     target_collection_name = "Scrapes"

#     # Connect to MongoDB with the specified collection name
#     client, collection = connect_to_mongodb(target_collection_name)

#     # If the connection is successful, proceed to insert the document
#     if client is not None and collection is not None:
#         insert_document(collection, new_document)

#     # Close the MongoDB connection
#     if client is not None:
#         close_connection(client)