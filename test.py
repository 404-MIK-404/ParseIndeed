import psycopg2
import undetected_chromedriver
import time
import math
import string

from bs4 import BeautifulSoup


querySearch = 'junior product analyst'
country = ""
l = ('remote ' + country).strip()

conn = psycopg2.connect(
    host="dpg-ci4cagmnqql46qqq91o0-a.oregon-postgres.render.com",
    port="5432",
    database="analitic2023",
    user="analitic2023_user",
    password="tATQkPfauIlSEZDOBilddYaqncprR6zM")

cursor = conn.cursor()


def getUrlNoPar(position, function, country):
    template = 'https://www.indeed.com/jobs?q={}&l={}&rbl={}'
    url = template.format(position, function, country)
    return url


def getUrlStart(position, function, start, country):
    template = 'https://www.indeed.com/jobs?q={}&l={}&rbl={}&start={}'
    url = template.format(position, function, start, country)
    return url


def getResultParseIndeed(result):
    urlJob = result.find("a", id=lambda x: x and x.startswith('job_'))

    finalResult = {
        "name": result.find("span", id=lambda x: x and x.startswith('jobTitle')).text or "empty",
        "companyName": result.find("span", {"class": "companyName"}) or "unknown",
        "ratingCompany": result.find("span", attrs={"aria-hidden": "true", "class": ""}) or "empty",
        "location": result.find("div", {"class": "companyLocation"}).text or "empty",
        "attr": result.find("div", {"class": "attribute_snippet"}) or "empty",
        "date": result.find("span", {"class": "date"}).text,
        "urlJob": "https://www.indeed.com" + urlJob.attrs['href'],
        "snippetRes": getSnippetRest(result.find_all("li", {"class": "", "id": ""}))
    }

    finalResult['snippetRes'] = finalResult['snippetRes'][:-2 - 1]

    if finalResult['companyName'] != "unknown":
        finalResult['companyName'] = finalResult['companyName'].text

    if finalResult['ratingCompany'] != "empty":
        finalResult['ratingCompany'] = finalResult['ratingCompany'].text

    if finalResult['attr'] != "empty":
        finalResult['attr'] = finalResult['attr'].text

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
        url = getUrlStart(querySearch, l, 10 * i, country)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        myUl = soup.find_all("div", {"class": "job_seen_beacon"})
        if myUl is None:
            while True:
                soup = BeautifulSoup(driver.page_source, 'lxml')
                myUl = soup.find_all("div", {"class": "job_seen_beacon"})
                if myUl is not None:
                    break
                time.sleep(50)
        else:
            for val in myUl:
                resVal = getResultParseIndeed(val)
                result.append(resVal)
            i += 1
    return result


url = getUrlNoPar(querySearch, l, country)

driver = undetected_chromedriver.Chrome()

try:
    driver.get(url)
    time.sleep(50)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    myUl = soup.find_all("div", {"class": "job_seen_beacon"})
    countJobs = soup.find("div", {"class": "jobsearch-JobCountAndSortPane-jobCount"})
    jobs = countJobs.find("span", {"class": "", "id": ""}).text.replace('jobs', '').strip()
    print("Count jobs: " + jobs)
    records = []

    for result in myUl:
        resultParse = getResultParseIndeed(result)
        records.append(resultParse)

    resss = getResultParseIndeedSearch(int(jobs))
    records += resss

    for test in records:
        driver.get(test["urlJob"])
        soup = BeautifulSoup(driver.page_source, 'lxml')
        fullDescr = soup.find("div", {"id": "jobDescriptionText"})
        if fullDescr is None:
            while True:
                soup = BeautifulSoup(driver.page_source, 'lxml')
                fullDescr = soup.find("div", {"id": "jobDescriptionText"})
                if fullDescr is not None:
                    break
                time.sleep(50)
        else:
            test["snippetRes"] = fullDescr.text
            cursor.execute(
                "INSERT INTO parseindeedusa (name,companyname,ratingcompany,location,attr,date,urljob,snippetres) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (test["name"], test["companyName"], test["ratingCompany"], test["location"],
                 test["attr"], test["date"], test["urlJob"], test["snippetRes"])
            )
            conn.commit()

except Exception as ex:
    print(ex)
finally:
    cursor.close()
    conn.close()
    driver.close()
    driver.quit()
