import requests
import json
from bs4 import BeautifulSoup
import fake_headers

## вакансии --> <div data-qa="vacancy-serp__results" id="a11y-main-content">
## заголовок вакансия --> <h3 data-qa="bloko-header-3" class="bloko-header-section-3">< 
## ссылка --> <a class="serp-item__title" data-qa="serp-item__title">
## зп --> <span data-qa="vacancy-serp__vacancy-compensation" class="bloko-header-section-2">
## название компании --> <div class="vacancy-serp-item-company"> OR <div class="vacancy-serp-item__meta-info-company">
## город --> <div data-qa="vacancy-serp__vacancy-address" class="bloko-text">
## описание вакансии --> <div class="g-user-content" data-qa="vacancy-description">

KEYWORDS = ['Django', 'Flask']
URL = 'https://spb.hh.ru/search/vacancy?text=Python&area=1&area=2'

headers_gen = fake_headers.Headers(browser="firefox", os="win")

# получение данных по вакансиям
response = requests.get(URL, headers=headers_gen.generate())
html_data = response.text
hh_main = BeautifulSoup(html_data, 'lxml')

vacancy_list = hh_main.find('div', id="a11y-main-content")

vacancy_parsed = []
for vacancy_tag in vacancy_list:
    vacancy_info = {}

    #  ссылка на описание вакансии
    if vacancy_tag.find('a', class_='serp-item__title') is not None:
        link = vacancy_tag.find('a', class_='serp-item__title')['href']

        # загрузка описания вакансии из ссылки на осписание вакансии
        vacancy_response = requests.get(link, headers=headers_gen.generate())
        description = BeautifulSoup(vacancy_response.text, "lxml")
        vacancy_body_tag = description.find("div", class_="g-user-content")
        vacancy_body_text = vacancy_body_tag.text

        # проверка на ключевые слова в описании вакансии и заполнение славаря vacancy_info
        if any(keyword.lower() in vacancy_body_text.lower() for keyword in KEYWORDS):
            vacancy = vacancy_tag.find('h3', class_='bloko-header-section-3').text
            vacancy_info['vacancy'] = vacancy

            vacancy_info['link'] = link
            vacancy_info['description'] = vacancy_body_text

            if vacancy_tag.find('span', class_='bloko-header-section-2') is not None:
                salary = vacancy_tag.find('span', class_='bloko-header-section-2').text
                vacancy_info['salary'] = salary

            company = vacancy_tag.find('div', class_='vacancy-serp-item-company').text
            vacancy_info['company'] = company
                  
            if vacancy_tag.find('div', 'div data-qa="vacancy-serp__vacancy-address') is not None: 
                city = vacancy_tag.find('div', 'div data-qa="vacancy-serp__vacancy-address').text
                vacancy_info['city'] = city

    if len(vacancy_info) != 0:
        vacancy_parsed.append(vacancy_info)


with open('vacancies.json', 'w', encoding='utf-8') as file:
    json.dump(vacancy_parsed, file, ensure_ascii=False, indent=4)