import requests
import time
from bs4 import BeautifulSoup

def scrape_routes(soup, region, routes):
    for tag in soup.find_all("a"):
        link = tag.get("href", "").casefold()
        if link and link.startswith(f"/{region}/course") and link not in routes[region]:
            routes[region].append(news_url + link)

def scrape_courses(region_code):
    url = f"{news_url}/{region_code}/products/training"
    routes = {region_code: [url]}
    course_infos = []

    for route_url in routes[region_code]:
        response = requests.get(route_url)
        print(response, route_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            scrape_routes(soup, region_code, routes)

            course_name = soup.title.string

            for element in soup.select("div[id='course-offering-tbl'] div.row.pt-2.pb-2"):
                course_contents = list(filter(lambda x: not isinstance(x, str), element.contents))
                course_date, course_location = course_contents[1].string, course_contents[2].string
                course_price = float(course_contents[3].string.split()[1].replace(",", ""))
                course_currency = "CAD" if region_code == "en-ca" else "USD"
                course_id = int(course_contents[4].a.get("href").split("/")[-2])

                if course_date != "Anytime": 
                    course_infos.append(
                        {
                            "region code": region_code,
                            "id": course_id,
                            "url": route_url,
                            "course": course_name,
                            "currency": course_currency,
                            "date": course_date,
                            "location": course_location,
                            "price": course_price,
                        }
                    )
        else:
            print("Failed to retrieve the page.")
    
    return course_infos

def export_csv(course_infos):
    obj = time.localtime()
    csv_filename = f"./data/proceed/courses_overview_{obj.tm_year}_{obj.tm_mon}_{obj.tm_mday}.csv"

    with open(csv_filename, "w") as course_file:
        course_file.write("Region, Course, Date, Price, Id, Location, Currency, URL \n")
        for info in course_infos:
            course_file.write(
                f"{info['region code']}, {info['course']}, {info['date']}, {info['price']}, {info['id']}, {info['location']}, {info['currency']}, {info['url']} \n"
            )

if __name__ == "__main__":
    news_url = "https://www.pinkelephant.com"
    region_codes = ["en-us", "en-ca"]
    course_infos = []

    for region_code in region_codes:
        course_infos.extend(scrape_courses(region_code))

    export_csv(course_infos)