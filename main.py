import requests
import csv
import time
from bs4 import BeautifulSoup


def scrape_routes(soup, region):
    a_tags = soup.find_all("a")
    print(region)
    for tag in a_tags:
        link = tag.get("href", "").casefold()
        if link and link not in routes[region]:
            new_route = news_url + link
            routes[region].append(new_route) if link.startswith(
                f"/{region}/course"
            ) and new_route not in routes[region] else ""


def scrape_courses(region_code):
    url = news_url + '/' + f'{region_code}/products/training'
    routes.update({region_code: [url]})
    
    for url in routes[region_code]:
        response = requests.get(url.casefold())
        print(response, url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            scrape_routes(soup, region_code)
            # print(routes)
            for element in soup.find_all("div", id = 'course-offering-tbl'):
                # course_name = element.select('div.course-offering-title')[0].string[17:]
                course_name = soup.title.string
                course_carts = element.select('div.row.pt-2.pb-2')
                for detail in course_carts:
                    course_contents =  list(filter(lambda x: not isinstance(x, str), detail.contents))
                    # print(course_contents)
                    course_date = course_contents[1].string
                    course_location = course_contents[2].string
                    course_price = float(course_contents[3].string.split()[1].replace(',', ''))
                    # print(float(course_contents[3].string.split()[1].replace(',', '')))
                    course_currency = ('USD', 'CAD') [region_code == 'en-ca']
                    course_id = [int(x) for x in course_contents[4].a.get('href').split('/') if x.isdigit()][0]
                    if course_date != 'Anytime': 
                        course_infos.append(
                            {"region code": region_code, "id": course_id, "url": url, "course": course_name, "currency": course_currency, "date": course_date, "location": course_location, "price": course_price}
                        )
                        # course_infos += f'{course_name}, {course_date}, {course_price}, {course_id}, {course_location}, {course_currency}, {url} \n'
        else:
            print("Failed to retrieve the page.")
    
    return course_infos
                
def write_csv ():
    course_matrix = ''
    for info in course_infos:
        # print(info)
        course_matrix += f'{info["region code"]}, {info["course"]}, {info["date"]}, {info["price"]}, {info["id"]}, {info["location"]}, {info["currency"]}, {info["url"]} \n'
    return course_matrix

def export_csv ():
    obj = time.localtime()
    with open(f'./data/proceed/courses_overview_{obj.tm_year}_{obj.tm_mon}_{obj.tm_mday}.csv', 'w') as course_file:
        course_file.write('Region, Course, Date, Price, Id, Location, Currency, URL \n')
        course_file.write(write_csv())
    

if __name__ == "__main__":
    news_url = "https://www.pinkelephant.com"
    region_codes = 'en-us', 'en-ca'
    routes = dict()
    course_infos = []
    list(map (scrape_courses, region_codes))
    # course_infos = ''
    export_csv()
    
    

    # print(routes, course_infos)
