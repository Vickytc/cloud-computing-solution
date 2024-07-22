"""
Script Name: AsyncFissionClient.py
Description: Async way to retrieve data from Elasticsearch 
Authors:
    Luxi Bai(1527822)
    Wenxin Zhu (1136510)
    Ze Pang (955698) 
"""

import asyncio
import aiohttp
import json
import pandas as pd
import logging
import os


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AsyncFissionClient:
    def __init__(self, base_url="http://localhost:9090"):
        self.base_url = base_url


    async def fetch_to_json(self, session, url):
        """Fetch a single URL."""
        try:
            logging.info("Requesting URL: %s", url)
            async with session.get(url) as response:
                # Raise HTTPError for bad responses
                response.raise_for_status()  
                response_str = await response.text()
                response_json = json.loads(response_str)
                filename = url.replace(self.base_url,"").replace("/keyword","").replace("/start","").replace("/end","").replace("/size","")[1:].replace("/","_")
                os.makedirs("./es_data", exist_ok=True)
                with open(f"es_data/{filename}.json", 'w', encoding='utf-8') as json_file:
                    json.dump(response_json, json_file, indent=4)
                logging.info("Data saved to %s", filename)
                return response_json, response.status
        except aiohttp.ClientError as e:
            logging.error("HTTP Request failed: %s", e)
            raise
        except Exception as e:
            logging.error("An error occurred: %s", e)
            raise


    async def fetch_all_to_json(self, urls):
        """Fetch multiple URLs concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_to_json(session, url) for url in urls]
            return await asyncio.gather(*tasks)


    def build_url(self, endpoint, params):
        """Helper function to build URLs for requests."""
        url = f"{self.base_url}/{endpoint}/{params['server']}"
        if 'keyword' in params:
            url += f"/keyword/{params['keyword']}"
        if 'start' in params and 'end' in params:
            url += f"/start/{params['start']}/end/{params['end']}"
        if 'size' in params:
            url += f"/size/{params['size']}"
        return url


    async def search(self, params):
        """Search documents from the server based on keyword and optional date range and size."""
        url = self.build_url('search', params)
        return await self.fetch_all_to_csv([url])

    async def word_cloud(self, params):
        """Generate a word cloud from the server based on keyword and optional date range and size."""
        url = self.build_url('wordcloud', params)
        return await self.fetch_all_to_csv([url])

    async def retrieve(self, server):
        """Retrieve documents from the server."""
        url = f"{self.base_url}/retrieve/{server}"
        return await self.fetch_all_to_csv([url])


async def main():
    client = AsyncFissionClient()
    servers = ["twitter", "mastodon"]
    keywords = ["Telstra", "Optus", "Vodafone", "EV", "Tesla", "BYD", "5G", "AI"]
    search_urls = [
        # client.build_url('search', {"server": server, "keyword":keyword})
        # for server in servers for keyword in keywords
    ]
    wordcloud_urls = [
        # client.build_url('wordcloud', {"server": server, "keyword":keyword})
        # for server in servers for keyword in keywords
    ]
    retrieve_urls = [client.build_url('retrieve', {"server": "sites"})]
    urls = search_urls + wordcloud_urls + retrieve_urls
    try:
        results = await client.fetch_all_to_json(urls)
        for _, status in results:
            logging.info("Request successful, status code: %d", status)
    except Exception as e:
        logging.error("An error occurred during requests: %s", e)

if __name__ == "__main__":
    asyncio.run(main())
