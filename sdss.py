from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from dateutil import parser
import icalendar
from datetime import timedelta
import datetime
import argparse

#make event function
def make_event(item_list):
    event = icalendar.Event()
    print(item_list[0],item_list[1],item_list[2])

    event.add('summary', item_list[0])
    event.add('dtstart', item_list[1])
    event.add('dtend', item_list[1] + timedelta(hours=1.5))
    event.add('location', item_list[2])

    return event

#main, works from command line
def main():
    app = argparse.ArgumentParser(description="Scrape sundevilsync and make an ics file of the data")
    app.add_argument(
        "url", 
        help="the url for the relevant events page"
    )
    app.add_argument(
        "filename", 
        help="the name of the outputted ics file"
    )
    args = app.parse_args()

    # Set up Selenium WebDriver (use ChromeDriver as an example)
    driver = webdriver.Chrome()  # Make sure the ChromeDriver executable is in your PATH

    # URL to scrape
    url = args.url

    # Load the page
    driver.get(url)

    # Wait for the page to load (adjust the sleep time as needed)
    time.sleep(2)

    # Get the fully rendered page source
    page_source = driver.page_source

    # Parse with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all <h3> elements with specific style
    titles = soup.find_all('h3', style=lambda s: s and 'font-size: 1.06rem' in s)

    # Find div elements with datetime and location 
    dtps = soup.find_all('svg', style="display: inline-block; color: rgba(0, 0, 0, 0.87); fill: currentcolor; height: 1.313rem; width: 0.875rem; user-select: none; transition: 450ms cubic-bezier(0.23, 1, 0.32, 1); float: left; margin: 0px 0.25rem 0px 0px; position: relative; opacity: 0.85;")

    # Save text of matching info. Pos 1 = name. Pos 2 = datetiem. Pos 3 = place.
    all_events = []

    for title in titles:
        info = []
        info.append(title.get_text(strip=True))
        all_events.append(info)

    #index2 is for the data list
    index = 0
    for event in all_events:
        #c is the count which indicates whether it's date or place
        c = 0
        while c < 2:
            data = dtps[index].parent.get_text(strip=True)
            if c == 0:
                parsed_datetime = parser.parse(data)
                event.append(parsed_datetime)
            else:
                event.append(data)
            c = c + 1
            index = index + 1

    #make calendar
    cal = icalendar.Calendar()
    cal.add('prodid', '-//ASU club calendar//')
    cal.add('version', '2.0')

    for item in all_events:
        event = make_event(item)
        cal.add_component(event)

    # Write the calendar to an .ics file
    with open(args.filename, 'wb') as f:
        f.write(cal.to_ical())

    print(f"Saved as: {args.filename}.ics")

    # Quit the driver
    driver.quit()

if __name__ == "__main__":
    main()