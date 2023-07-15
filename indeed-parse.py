import requests
import psycopg2
import math
from bs4 import BeautifulSoup


def getUrlNoPar(position, function, country):
    template = 'https://www.indeed.com/jobs?q={}&l={}&rbl={}'
    url = template.format(position, function, country)
    return url


def getUrlStart(position, function, start, country):
    template = 'https://www.indeed.com/jobs?q={}&l={}&rbl={}&start={}'
    url = template.format(position, function, start, country)
    return url


def getUrlRequest(url):
    return requests.get(url_request_pars.format(API_WEB, url))


def getResultParseIndeed(result,soup):
    urlJob = result.find("a", {"class": "jcs-JobTitle"})

    finalResult = {
        "name": result.find("span", id=lambda x: x and x.startswith('jobTitle')).text or "empty",
        "companyName": result.find("span", {"class": "companyName"}) or "unknown",
        "ratingCompany": result.find("span", attrs={"aria-hidden": "true", "class": ""}) or "empty",
        "location": result.find("div", {"class": "companyLocation"}).text or "empty",
        "attr": result.find("div", {"class": "attribute_snippet"}) or "empty",
        "date": result.find("span", {"class": "date"}) or "empty",
        "urlJob": "https://www.indeed.com" + urlJob.attrs['href'],
        "snippetRes": soup.find("div", {"id": "jobDescriptionText"})
    }

    #finalResult['snippetRes'] = finalResult['snippetRes'][:-2 - 1]

    if finalResult['companyName'] != "unknown":
        finalResult['companyName'] = finalResult['companyName'].text.strip()

    if finalResult['ratingCompany'] != "empty":
        finalResult['ratingCompany'] = finalResult['ratingCompany'].text.strip()

    if finalResult['attr'] != "empty":
        finalResult['attr'] = finalResult['attr'].text.strip()

    if finalResult['date'] != "empty":
        finalResult['date'] = finalResult['date'].text.strip()

    return finalResult


def getSnippetRest(result):
    res = ""
    for value in result:
        res += value.text + " "
    return res


def getResultParseIndeedSearch(countJobs):
    numb = math.ceil(countJobs / 24)
    i = 1
    result = []
    while i < numb:
        url_indeed = getUrlStart(querySearch, l, 10 * i, country)
        response = getUrlRequest(url_indeed)
        soup = BeautifulSoup(response.content, 'lxml')
        myUl = soup.find_all("div", {"class": "job_seen_beacon"})
        for val in myUl:
            resVal = getResultParseIndeed(val)
            result.append(resVal)
        i += 1
    return result


API_WEB = "8250d2e2d11042d2aed259e9eeae7a7f&"

querySearch = 'data analyst'
country = "USA"
l = ('' + country).strip()

conn = psycopg2.connect(
    host="dpg-ci4cagmnqql46qqq91o0-a.oregon-postgres.render.com",
    port="5432",
    database="analitic2023",
    user="analitic2023_user",
    password="tATQkPfauIlSEZDOBilddYaqncprR6zM")

cursor = conn.cursor()

url_request_pars = "https://scrape.abstractapi.com/v1/?api_key={}&url={}"

try:
    url_indeed = getUrlNoPar(querySearch, l, country)
    response = getUrlRequest(url_indeed)
    soup = BeautifulSoup(response.content, 'lxml')
    myUl = soup.find_all("div", {"class": "cardOutline"})
    countJobs = soup.find("div", {"class": "jobsearch-JobCountAndSortPane-jobCount"})
    jobs = countJobs.find("span", {"class": "", "id": ""}).text.replace('jobs', '').strip().replace(",","")
    print("Count jobs: " + jobs)
    records = []

    for result in myUl:
        resultParse = getResultParseIndeed(result,soup)
        records.append(resultParse)

    resss = getResultParseIndeedSearch(int(jobs))
    records += resss

    for test in records:
        responseJobUrl = getUrlRequest(test["urlJob"])
        soup = BeautifulSoup(responseJobUrl.content, 'lxml')
        fullDescr = soup.find("div", {"id": "jobDescriptionText"})
        test["snippetRes"] = fullDescr.text
        cursor.execute(
            "INSERT INTO parseindeedusa (name,companyname,ratingcompany,location,attr,date,urljob,snippetres) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (test["name"], test["companyName"], test["ratingCompany"], test["location"],
            test["attr"], test["date"], test["urlJob"], test["snippetRes"])
        )
        conn.commit()
finally:
    cursor.close()
    conn.close()

# print(response.status_code)
# print(response.content)
