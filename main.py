import requests
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

# tutorials: https://www.youtube.com/watch?v=fKl2JW_qrso

def request_handle(route_url):
    response = requests.get(route_url)
    print(response, route_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        return soup
    else:
        print("Failed to retrieve the page.")
        return None
    
def scrape_routes(region, route):
    soup = request_handle(route)
    if soup:
        for tag in soup.find_all("a"):
            link = tag.get("href", "").casefold()
            full_link = news_url + link
            if (
                link
                and link.startswith(f"/{region}/course")
                and (link not in routes[region] and full_link not in routes[region])
            ):
                routes[region].add(full_link)
    else: raise ConnectionError('Failed to connect to the page')


def scrape_course_info(region_code, route):
    
    soup = request_handle(route)

    if soup:
        course_name = soup.title.string.replace(",", " ")

        # process only in course detail page
        for element in soup.select("div[id='course-offering-tbl'] div.row.pt-2.pb-2"):
            course_contents = list(
                filter(lambda x: not isinstance(x, str), element.contents)
            )
            course_date, course_location = (
                course_contents[1].string,
                course_contents[2].string,
            )
            course_price = float(course_contents[3].string.split()[1].replace(",", ""))
            course_currency = "CAD" if region_code == "en-ca" else "USD"
            course_id = int(course_contents[4].a.get("href").split("/")[-2])

            if course_date != "Anytime":
                course_infos.append(
                    {
                        "region code": region_code,
                        "id": course_id,
                        "url": route,
                        "course": course_name,
                        "currency": course_currency,
                        "date": course_date,
                        "location": course_location,
                        "price": course_price,
                    }
                )
    else:
        print("Failed to retrieve the page.")


def export_csv(course_infos):
    obj = time.localtime()
    csv_filename = (
        f"./data/proceed/courses_overview_{obj.tm_year}_{obj.tm_mon}_{obj.tm_mday}.csv"
    )

    with open(csv_filename, "w") as course_file:
        course_file.write("Region, Course, Date, Price, Id, Location, Currency, URL \n")
        for info in course_infos:
            course_file.write(
                f"{info['region code']}, {info['course']}, {info['date']}, {info['price']}, {info['id']}, {info['location']}, {info['currency']}, {info['url']} \n"
            )


if __name__ == "__main__":
    start = time.perf_counter()
    news_url = "https://www.pinkelephant.com"
    region_codes = ["en-us", "en-ca"]
    global routes
    routes = {region_code: set() for region_code in region_codes}
    course_infos = []
    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            for region_code in region_codes:
                base_url = f"{news_url}/{region_code}/products/training"
                routes[region_code].add(base_url)
                
                futures = [executor.submit(scrape_routes, region_code, route) for route in routes[region_code]]

                wait(futures, return_when=ALL_COMPLETED)
                # append to course_infos
                executor.map(
                    scrape_course_info,
                    [region_code] * len(routes[region_code]),
                    routes[region_code],
                )
        # print(course_infos)
        export_csv(course_infos)
    except Exception as error:
        print(f'{error}')

    finish = time.perf_counter()
    print(f"Finish in {round(finish - start, 2)} secs")
