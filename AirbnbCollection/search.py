import asyncio
import re
from urllib.parse import urljoin
from playwright.async_api import async_playwright
import random
import time

async def scrape_airbnb_properties(url):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)  # Set headless to False for debugging
        context = await browser.new_context()

        try:
            page = await context.new_page()
            await page.goto(url)

            # Wait for the element containing "Search results" to be present
            await page.wait_for_selector('//span[contains(text(), "Search results")]')

            # Use evaluate to get the sibling text
            result_text = await page.evaluate(
                '''() => {
                    const xpathResult = document.evaluate('//span[contains(text(), "Search results")]/following-sibling::text()', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                    const textNode = xpathResult.singleNodeValue;
                    return textNode ? textNode.textContent.trim() : null;
                }'''
            )

            # print(f"Results: {result_text}")

            # Use a regular expression to match and extract digits
            match = re.search(r'(?:Over\s)?(\d{1,3}(?:,\d{3})*|\d+)', result_text)

            # Check if a match is found
            if match:
                # Convert the matched string to an integer
                total_listings_found = int(match.group(1).replace(',', ''))

                # Use the numeric value as needed
                # print("Numeric Value:", total_listings_found)
            # else:
            #     print("No numeric value found in the result text")

            # Loop through the pages recording all the listings
            results = []
            page_number = 1
            results.append({
                'page_number': page_number,
                'page_results': []
            })
             # Use evaluate to get a list of all meta elements with "/rooms/" in the content attribute
            listing_urls = await page.evaluate('''() => {
                const metaElements = document.querySelectorAll('meta[itemprop="url"]');
                const listingUrls = Array.from(metaElements, element => element.content.trim());
                return listingUrls.filter(url => url.includes("/rooms/"));
            }''')

            # Process each listing URL
            listings_recorded = 0
            for i, listing_url in enumerate(listing_urls, start=1):
                # Find the start index of the ID
                start_index = listing_url.find("/rooms/") + len("/rooms/")

                # Extract the ID
                listing_id = listing_url[start_index:].split('?')[0]

                # print("Listing ID:", listing_id)
                results[page_number-1]["page_results"].append(listing_id)
                listings_recorded += 1

            # If there are listings still not recorded, there should be another page and wait for that button
            if listings_recorded < total_listings_found:
                await page.wait_for_selector('a[aria-label="Next"]')

            # While there is a next page, go to it and record the listings

            #Get the next button
            next_button = await page.query_selector('a[aria-label="Next"]')

            while next_button:

                # Random sleep period between 0.5 and 2 seconds
                sleep_duration = random.uniform(0.5, 2)
                # print(f"Sleeping for {sleep_duration:.2f} seconds.")
                time.sleep(sleep_duration)
                
                # print("Next page")

                await next_button.click()

                page_number += 1
                results.append({
                    'page_number': page_number,
                    'page_results': []
                })

                # Get the listings for the next page
                
                # Wait for the element containing "Search results" to be present
                await page.wait_for_selector('//span[contains(text(), "Search results")]')

                listing_urls = await page.evaluate('''() => {
                    const metaElements = document.querySelectorAll('meta[itemprop="url"]');
                    const listingUrls = Array.from(metaElements, element => element.content.trim());
                    return listingUrls.filter(url => url.includes("/rooms/"));
                }''')

                # Process each listing URL
                for i, listing_url in enumerate(listing_urls, start=1):
                    # Find the start index of the ID
                    start_index = listing_url.find("/rooms/") + len("/rooms/")

                    # Extract the ID
                    listing_id = listing_url[start_index:].split('?')[0]

                    # print("Listing ID:", listing_id)
                    results[page_number-1]["page_results"].append(listing_id)
                    listings_recorded += 1


                # # See if there should be another next page
                # print(listings_recorded, total_listings_found)
                if listings_recorded < total_listings_found and listings_recorded < 270:
                    await page.wait_for_selector('a[aria-label="Next"]')
                    next_button = await page.query_selector('a[aria-label="Next"]')
                else:
                    next_button = None



                
            # print("No more pages available.")

            # print(results)

            # }

            # Keep the browser open for inspection
            # await page.pause()

        except Exception as e:
            print(f"Error: {e}")
            # An error came up in scraping, could possibly be no search results were found, return any results that were collected or empty otherwise
            # print("Setting empty")

            if 'listings_recorded' not in locals():
                listings_recorded = 0
            if 'results' not in locals():
                results = []
            if 'total_listings_found' not in locals():
                total_listings_found = 0
            
            print(listings_recorded, total_listings_found, results)
        finally:
            # Comment out the line below to keep the browser open
            print(listings_recorded, total_listings_found, len(results))
            await browser.close()
            return results, listings_recorded, total_listings_found

# # Example URL
# airbnb_url = "https://www.airbnb.ae/s/United-Arab-Emirates/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&price_filter_input_type=0&channel=EXPLORE&query=United%20Arab%20Emirates&adults=1&source=structured_search_input_header&search_type=user_map_move&ne_lat=25.866849553545304&ne_lng=56.107806650099064&sw_lat=23.256642736910624&sw_lng=53.68342192464783&zoom=8.047495163091876&zoom_level=8.047495163091876&search_by_map=true"
# 761 listings
# airbnb_url = "https://www.airbnb.ae/s/United-Arab-Emirates/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&price_filter_input_type=0&channel=EXPLORE&query=United%20Arab%20Emirates&adults=1&source=structured_search_input_header&search_type=user_map_move&ne_lat=24.52743480283826&ne_lng=54.442760874360545&sw_lat=24.395174645771792&sw_lng=54.338766248809236&zoom=12.30262889805887&zoom_level=12.30262889805887&search_by_map=true&place_id=ChIJvRKrsd9IXj4RpwoIwFYv0zM&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2023-12-01&monthly_length=3&price_filter_num_nights=5"

# # 79 listings
# airbnb_url = "https://www.airbnb.ae/s/United-Arab-Emirates/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&price_filter_input_type=0&channel=EXPLORE&query=United%20Arab%20Emirates&adults=1&source=structured_search_input_header&search_type=user_map_move&ne_lat=24.486571934981825&ne_lng=54.62279642529387&sw_lat=24.478865894582416&sw_lng=54.61673622632355&zoom=16.40362889805915&zoom_level=16.40362889805915&search_by_map=true&place_id=ChIJvRKrsd9IXj4RpwoIwFYv0zM&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2023-12-01&monthly_length=3&price_filter_num_nights=5"
# airbnb_url = "https://www.airbnb.ae/s/United-Arab-Emirates/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&price_filter_input_type=0&channel=EXPLORE&query=United%20Arab%20Emirates&adults=1&source=structured_search_input_header&search_type=user_map_move&ne_lat=24.486571934981825&ne_lng=54.62279642529387&sw_lat=24.478865894582416&sw_lng=54.61673622632355&search_by_map=true&place_id=ChIJvRKrsd9IXj4RpwoIwFYv0zM"

# # Run the scraper
# scrape_results, scrape_count = asyncio.run(scrape_airbnb_properties(airbnb_url))
# print("Results",scrape_results,scrape_count)

# # Record scrape results to mongoDB


# # If there are more than 270 results, subdivide and rerun scrape
