from bs4 import BeautifulSoup
import requests
import pandas as pd

def scrape_jobs(course_title, page_num, save_path):
    url = f"https://www.linkedin.com/jobs/search?keywords={course_title}&location=Worldwide&geoId=92000000&f_TPR=&position=1&pageNum={page_num}"
    id_list = []

    page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, "html.parser")
        pay_jobs = soup.find_all("li")
        for jobs in pay_jobs:
            base_card_div = jobs.find("div", {"class": "base-card"})
            if base_card_div and base_card_div.get("data-entity-urn"):
                job_id = base_card_div.get("data-entity-urn").split(":")[3]
                id_list.append(job_id)

    job_list = []
    for job_id in id_list:
        job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
        job_response = requests.get(job_url, headers={'User-Agent': 'Mozilla/5.0'})
        job_soup = BeautifulSoup(job_response.text, "html.parser")
        job_post = {}

        try:
            job_title_tag = job_soup.find("h1") or job_soup.find("h2")
            job_post["job_title"] = job_title_tag.text.strip() if job_title_tag else None
        except:
            job_post["job_title"] = None

        try:
            company_tag = job_soup.find("a", class_="topcard__org-name-link")
            job_post["company_name"] = company_tag.text.strip() if company_tag else None
        except:
            job_post["company_name"] = None

        try:
            time_tag = job_soup.find("span", class_="posted-time-ago__text")
            job_post["time_posted"] = time_tag.text.strip() if time_tag else None
        except:
            job_post["time_posted"] = None

        try:
            num_app_tag = job_soup.find("span", class_="num-applicants__caption") or job_soup.find("figcaption", class_="num-applicants__caption")
            job_post["num_applicant"] = num_app_tag.text.strip() if num_app_tag else None
        except:
            job_post["num_applicant"] = None

        try:
            location_tag = job_soup.find("span", class_="topcard__flavor topcard__flavor--bullet")
            if not location_tag:
                for span in job_soup.find_all("span"):
                    if span.text and any(loc in span.text.lower() for loc in ["remote", "nigeria", "worldwide", "lagos", "united", "city", "states"]):
                        location_tag = span
                        break
            job_post["job_location"] = location_tag.text.strip() if location_tag else None
        except:
            job_post["job_location"] = None

        try:
            apply_button = job_soup.find("a", {
                "class": "top-card-layout__cta mt-2 ml-1.5 h-auto babybear:flex-auto top-card-layout__cta--secondary btn-md btn-secondary"
            })
            job_post["apply_link"] = apply_button["href"].strip() if apply_button else None
        except:
            job_post["apply_link"] = None

        job_list.append(job_post)

    jobs_df = pd.DataFrame(job_list)
    jobs_df.to_excel(save_path, index=False)
    return job_list
