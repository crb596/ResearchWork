from mongodb_operations import connect_to_mongodb, insert_document, close_connection
import asyncio
from bson import ObjectId


# From scrape results, import listings into the MongoDB listing collection

async def main():
    # ======== Connect to MongoDB ========
    
    # Specify the collection name
    target_collection_name = "Scrapes"

    # Connect to MongoDB with the specified collection name
    client, collection = connect_to_mongodb(target_collection_name)

    # Get all the documents we want to import in a range of ObjectIDS

    # 1079 Listings found
    # min_id = ObjectId("65644725e3290cde14ec1e58")
    # max_id = ObjectId("65644876e3290cde14ec1e64")

    # min_id = ObjectId("65645dc0c213c8ff1d58744e")
    # max_id = ObjectId("65645dfac213c8ff1d587452")

    # min_id = ObjectId("656469006b6001779737ad2b")
    # max_id = ObjectId("656469d46b6001779737ad35")

    # Large UAE wide search results
    min_id = ObjectId("65646b484ab08f7f2c3a9d21")
    max_id = ObjectId("65648f074ab08f7f2c3a9eaa")


    # Query for documents with _id greater than or equal to the min and less than or equal to the max
    result = collection.find({"_id": {"$gte": min_id, "$lte": max_id}})

    result_listings = []
    result_ids = {}

    # Print or process the result
    for document in result:
        for page in document["results"]:
            for result in page["page_results"]:
                # Make sure this listing has not already been counted in this scrape
                if result not in result_ids:
                    result_ids[result] = True
                    result_listings.append({
                        "property_id": result
                    })
                
    print("Found",len(result_listings),"properties to migrate")
    client.close()

    # Connect to listings collection and add results

    # Specify the collection name
    target_collection_name = "Properties"

    # Connect to MongoDB with the specified collection name
    client, collection = connect_to_mongodb(target_collection_name)

    added_count = 0
    # Loop through all the results and add them to 
    for propertyListing in result_listings:
        # Check to see if this property is already in "Properties" collection
        existing_document = collection.find_one({"property_id": propertyListing["property_id"]})
        if not existing_document:
            # Add this new entry
            insert_document(collection, propertyListing)
            added_count += 1

    print("Found",len(result_listings),"properties in the scrape and added",added_count,"to Properties")


    client.close()



if __name__ == "__main__":
    asyncio.run(main())