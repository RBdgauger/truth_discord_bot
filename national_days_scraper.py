import requests
import os
from datetime import date
from bs4 import BeautifulSoup

ARTICLES = ["the", "a", "an"]
PREPOSITIONS = [
    "in", "on", "at", "by", "with", "for", "of", "to", "from",
    "over", "under", "between", "among", "through", "around"]
CONJUNCTIONS = ["and", "but", "or", "so", "yet", "for", "nor"]


FACTS_ELEM_TYPE = DATES_ELEM_TYPE = BIRTHDAYS_ELEM_TYPE = DEATHS_ELEM_TYPE = DAYS_ELEM_TYPE = "h3"

FACTS_CLASS = "gb-headline-9b8b6052"
DATES_CLASS = "gb-headline-c9c17c19"
BIRTHDAYS_CLASS = "gb-headline-288ec7a2"
DEATHS_CLASS = "gb-headline-343ac09b"
DAYS_CLASS = "holiday-title"

MAX_FACTS = MAX_DATES = MAX_BIRTHDAYS = MAX_DEATHS = 5
MAX_DAYS = 15

DATE_TODAY = date.today().strftime('%B-%d').lower()
FACTS_URL = "https://www.thefactsite.com/day/today/"
DAYS_URL = "https://nationaltoday.com/" + DATE_TODAY + '-holidays/'

directory = os.path.dirname(__file__)
list_starter = '-'

DAYS_STORAGE_PATH = directory + "/national_days.txt"
BLURB_STORAGE_PATH = directory + "/national_day_blurb.txt"

BLANK_OUTPUT_ERROR_MSG = "Something probably went wrong... Please contact your local idiot who made this script: 'dirkyg'."

def HTML_to_ascii(text):
    return str(text.encode('ascii', 'ignore').decode('utf-8'))

def get_html_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        return HTML_to_ascii(html_content)
    except requests.exceptions.RequestException as e:
        print("Error fetching the page: {}".format(e))
        return ""

def standardize_capitalization(text_list):
    def is_excluded(word):
        return word in ARTICLES or word in PREPOSITIONS or word in CONJUNCTIONS

    for i, text in enumerate(text_list):
        words = text.split()
        for j, word in enumerate(words):
            lower_word = word.lower()
            if is_excluded(lower_word) and j != 0:
                words[j] = lower_word
            else:
                words[j] = word[0].upper() + word[1:].lower()
        text_list[i] = " ".join(words)
    return text_list

def scrape_text_by_element_and_class(html_content, element_type, class_name, is_national_days=False):
    soup = BeautifulSoup(html_content, 'html.parser')
    elements = soup.find_all(element_type, class_=class_name)
    text_list = [element.get_text() for element in elements]

    if is_national_days:
        text_list = standardize_capitalization(text_list)

    return text_list

def get_facts_output(unfinished_facts, unfinished_dates):
    if (len(unfinished_facts) == len(unfinished_dates)) and len(unfinished_facts) != 0 and len(unfinished_dates) != 0:
        finished_facts = list(zip(unfinished_facts, unfinished_dates))
        fact_output = ""
        for i, (fact, date) in enumerate(finished_facts):
            if i != 0:
                fact_output += " "
            fact_output += "{} in {}.".format(fact[:-1], date)
        return fact_output
    else:
        return ""

def get_birthdays_output(finished_birthdays):
    if len(finished_birthdays) != 0:
        birthday_output = "Today is "
        for i, birthday in enumerate(finished_birthdays):
            if len(finished_birthdays) == 1:
                birthday_output += "{}".format(birthday)
            elif i == len(finished_birthdays) - 2:
                birthday_output += "{}'s and ".format(birthday)
            elif i == len(finished_birthdays) - 1:
                birthday_output += "{}'s ".format(birthday)
            else:
                birthday_output += "{}'s, ".format(birthday)
        birthday_output += "birthday."
        return birthday_output
    else:
        return ""

def get_deaths_output(finished_deaths):
    if len(finished_deaths) != 0:
        death_output = "The following people died on this day: "
        for i, death in enumerate(finished_deaths):
            if len(finished_deaths) == 1:
                death_output += "{}".format(death)
            elif i == len(finished_deaths) - 2:
                death_output += "{} and ".format(death)
            elif i == len(finished_deaths) - 1:
                death_output += "{} ".format(death)
            else:
                death_output += "{}, ".format(death)
        death_output += "."
        return death_output
    else:
        return ""
            

if __name__ == "__main__":
    fact_html_content = get_html_content(FACTS_URL)
    days_html_content = get_html_content(DAYS_URL)
    
    unfinished_facts = scrape_text_by_element_and_class(fact_html_content, FACTS_ELEM_TYPE, FACTS_CLASS)[:MAX_FACTS]
    unfinished_dates = scrape_text_by_element_and_class(fact_html_content, DATES_ELEM_TYPE, DATES_CLASS)[:MAX_DATES]

    finished_birthdays = scrape_text_by_element_and_class(fact_html_content, BIRTHDAYS_ELEM_TYPE, BIRTHDAYS_CLASS)[:MAX_BIRTHDAYS]
    finished_deaths = scrape_text_by_element_and_class(fact_html_content, DEATHS_ELEM_TYPE, DEATHS_CLASS)[:MAX_DEATHS]

    national_days = scrape_text_by_element_and_class(days_html_content, DAYS_ELEM_TYPE, DAYS_CLASS, True)[:MAX_DAYS]
    facts_output = get_facts_output(unfinished_facts, unfinished_dates)
    birthdays_output = get_birthdays_output(finished_birthdays)
    deaths_output = get_deaths_output(finished_deaths)

    if facts_output == "":
        facts_output = BLANK_OUTPUT_ERROR_MSG
    
    blurb_output = "{} {} {}".format(facts_output, birthdays_output, deaths_output)
    with open(DAYS_STORAGE_PATH, 'w') as days_file:
        for i, day in enumerate(national_days):
            list_starter = "{}.".format(i + 1)
            days_file.write("{} {}\n".format(list_starter, day))

    with open(BLURB_STORAGE_PATH, 'w') as blurb_file:
        blurb_file.write("Today in history...\n")
        blurb_file.write(blurb_output)
