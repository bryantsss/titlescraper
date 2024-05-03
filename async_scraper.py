import sys
import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def fetch_content(session, url):
    async with session.get(url) as response:
        return await response.text()

async def get_article_titles(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    article_titles = soup.find_all('h2', class_='card-title')
    return [title.text.strip() for title in article_titles]

async def get_next_api_url(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    button = soup.find('button', class_='btn btn-secondary btn-lg px-5 mb-5')
    if button:
        return button.get('hx-get')
    else:
        return None

async def scrape_realpython(url):
    async with aiohttp.ClientSession() as session:
        html = await fetch_content(session, url)
        soup = BeautifulSoup(html, 'html.parser')
        button = soup.find('button', class_='btn btn-secondary btn-lg px-5 mb-5')
        hx_get = button.get('hx-get')
        api_url = hx_get
        all_article_titles = []

        while api_url:
            async with session.get(f"https://realpython.com{api_url}") as response:
                content = await response.text()
                # Extract article titles
                article_titles = await get_article_titles(content)
                all_article_titles.extend(article_titles)
                # Get the next API URL
                api_url = await get_next_api_url(content)

        return all_article_titles

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python async_scraper.py <url> <output_file>")
        sys.exit(1)

    url = sys.argv[1]
    output_file = sys.argv[2]

    try:
        loop = asyncio.get_event_loop()
        article_titles = loop.run_until_complete(scrape_realpython(url))

        # Write article titles to the specified output file
        with open(output_file, 'w') as file:
            for title in article_titles:
                file.write(title + '\n')

        print("Article titles saved to", output_file)

    except Exception as e:
        print("An error occurred:", e)

