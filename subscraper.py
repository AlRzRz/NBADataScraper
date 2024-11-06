from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import routes
import time
import csv

COMBINE_ANTHRO = 'https://www.nba.com/stats/draft/combine-anthro?SeasonYear=2024&dir=A&sort=PLAYER_NAME'
COMBINE_AGILITY = 'https://www.nba.com/stats/draft/combine-strength-agility?SeasonYear=2024&dir=A&sort=PLAYER_NAME'
# csv_file = 'combineAnthro.csv'
csv_file = 'combineAgility.csv'

DROPDOWN_XPATH = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[1]/div/div[1]/div/label/div/select'
TBODY_XPATH = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table/tbody'


def convert_to_inches(data):
    def feet_inches_to_inches(feet_inches_str):
        try:
            # Split the string by the feet (') delimiter
            parts = feet_inches_str.split("'")
            if len(parts) < 2:
                raise ValueError(f"Unexpected format: {feet_inches_str}")
            
            # Parse feet and inches
            feet = int(parts[0].strip())
            inches = float(parts[1].replace("''", "").strip())
            
            # Convert to total inches
            total_inches = feet * 12 + inches
            return total_inches
        except ValueError as e:
            print(f"Error converting '{feet_inches_str}': {e}")
            return None  # or some default value like 0 if you prefer

    # Process the list items with the updated function
    result = [
        data[0],  # First item unaltered
        data[1],  # Second item unaltered
        feet_inches_to_inches(data[2]),  # Third item converted
        feet_inches_to_inches(data[3]),  # Fourth item converted
        data[4],  # Fifth item unaltered
        feet_inches_to_inches(data[5])   # Sixth item converted
    ]
    
    return result



def rowScrape(finalLst, rowIndex, year, driver):
    cargoLst = [year]
    retries = 3

    for attempt in range(retries):
        try:
            print(f"Attempting to scrape row data for year {year}, attempt {attempt + 1}")

            tbody = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, TBODY_XPATH))
            )

            rowTags = tbody.find_elements(By.TAG_NAME, 'tr')
            row = rowTags[rowIndex]

            dataElems = row.find_elements(By.TAG_NAME, 'td')
            print(f"Number of elements found in row: {len(dataElems)}")

            # Extract text for string elements
            strElems = [elem.text for elem in dataElems[:2]]
            # Extract text for float elements and pass as strings to convert_to_inches
            floatElems = [elem.text for elem in dataElems[2:7]]

            print("Accessing string elements:")
            for index, text in enumerate(strElems):
                print(f"String element {index}: {text}")
                cargoLst.append(text)

            print("Accessing float elements:")
            # cleanedFloats = convert_to_inches(floatElems)
            for index, value in enumerate(floatElems):
                print(f"Float element {index}: {value}")
                cargoLst.append(value)

            finalLst.append(cargoLst)
            break

        except (StaleElementReferenceException, IndexError) as e:
            if attempt < retries - 1:
                print(f"Stale element encountered in rowScrape (row for year {year}), retrying... Error: {e}")
                time.sleep(1)
            else:
                print(f"Failed to retrieve data after retries for row in year {year}. Error: {e}")



def seasonScrape(driver, finalLst, year):
  retries = 3
  for attempt in range(retries):
    try:
      print(f"Scraping page data for year {year}")
      tbody = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.XPATH, TBODY_XPATH))
      )

      rowTags = tbody.find_elements(By.TAG_NAME, 'tr')
      print(f"Number of rows found on page for year {year}: {len(rowTags)}")

      for rowIndex in range(len(rowTags)):
        print(f"Scraping row {rowIndex + 1} of {len(rowTags)} for year {year}")
        rowScrape(finalLst=finalLst, rowIndex=rowIndex, year=year, driver=driver)
    
      break
    except (StaleElementReferenceException, TimeoutException) as e:
      print(f"Error in pageScrape, retrying page for year {year}. Attempt {attempt + 1}. Error: {e}")
      time.sleep(2)



def mainScrape():
  
  start = time.time()

  driver = webdriver.Firefox()
  driver.get(COMBINE_AGILITY)
  driver.maximize_window()

  print('Process has commenced'.center(40, '~'))

  finalLst = []
  currentYr = 2024
  
  seasonScrape(driver, finalLst, currentYr)
  currentYr -= 1

  dropdown = driver.find_element(By.XPATH, DROPDOWN_XPATH)
  select = Select(dropdown)

  for index in range(1, len(select.options)):
    select.select_by_index(index)
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.XPATH, TBODY_XPATH))
    )

    seasonScrape(driver, finalLst, currentYr)
    print('Successfully scraped:', select.options[index].text)
    currentYr -= 1

  driver.quit()

#   headers = [
#     "YEAR", 
#     "PLAYER", 
#     "POS", 
#     "HAND LENGTH (Inches)", 
#     "HAND WIDTH (INCHES)", 
#     "HEIGHT W/O SHOES", 
#     "STANDING REACH", 
#     "WEIGHT (LBS)", 
#     "WINGSPAN"
# ]

  headers = [
     'YEAR',
     'PLAYER',
     'POS',
     'LANE AGILITY TIME (SECONDS)',
     'SHUTTLE RUN (SECONDS)',
     'THREE QUARTER SPRINT (SECONDS)',
     'STANDING VERTICAL LEAP (INCHES)',
     'MAX VERTICAL LEAP (INCHES)'
  ]


  with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    writer.writerow(headers)

    for row in finalLst:
      writer.writerow(row)

  print('Data successfully written to', csv_file)

  end = time.time()
  timeMinutes = (end - start) / 60
  print('\nTime Taken:', timeMinutes)

  driver.quit()



if __name__ == '__main__':
  mainScrape()