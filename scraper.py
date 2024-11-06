from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import routes
import time

def rowScrape(finalLst, rowIndex, year, driver):
    cargoLst = [year]
    retries = 3
    for attempt in range(retries):
        try:
            # Print to log the attempt and year being scraped
            print(f"Attempting to scrape row data for year {year}, attempt {attempt + 1}")

            # Re-fetch the row each time to avoid stale references
            tbody = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, routes.tableData['tableBody']))
            )
            rowTags = tbody.find_elements(By.TAG_NAME, 'tr')
            row = rowTags[rowIndex]  # Get the row by index

            # Locate elements within the row directly without re-fetching the row
            dataElems = row.find_elements(By.TAG_NAME, 'td')[1:]  # Skip the first if needed

            # Logging the number of elements found
            print(f"Number of elements found in row: {len(dataElems)}")

            strElems = dataElems[:2]
            floatElems = dataElems[2:]

            # Log before accessing string elements
            print("Accessing string elements:")
            for index, elem in enumerate(strElems):
                print(f"String element {index}: {elem.text}")
                cargoLst.append(elem.text)

            # Log before accessing float elements
            print("Accessing float elements:")
            for index, elem in enumerate(floatElems):
                print(f"Float element {index}: {elem.text}")
                cargoLst.append(float(elem.text))

            finalLst.append(cargoLst)
            break  # Exit retry loop if successful

        except (StaleElementReferenceException, IndexError) as e:
            if attempt < retries - 1:
                print(f"Stale element encountered in rowScrape (row for year {year}), retrying... Error: {e}")
                time.sleep(1)  # Small delay before retrying
            else:
                print(f"Failed to retrieve data after retries for row in year {year}. Error: {e}")


def pageScrape(driver, finalLst, year):
    retries = 3
    for attempt in range(retries):
        try:
            print(f"Scraping page data for year {year}")
            tbody = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, routes.tableData['tableBody']))
            )
            rowTags = tbody.find_elements(By.TAG_NAME, 'tr')
            print(f"Number of rows found on page for year {year}: {len(rowTags)}")

            for rowIndex in range(len(rowTags)):
                print(f"Scraping row {rowIndex + 1} of {len(rowTags)} for year {year}")
                rowScrape(finalLst=finalLst, rowIndex=rowIndex, year=year, driver=driver)

            break  # Exit retry loop if successful

        except (StaleElementReferenceException, TimeoutException) as e:
            print(f"Error in pageScrape, retrying page for year {year}. Attempt {attempt + 1}. Error: {e}")
            time.sleep(2)  # Small delay before retrying



def isButtonDisabled(driver, buttonXPATH):
    try:
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, buttonXPATH))
        )
        disabled_attribute = button.get_attribute('disabled')
        return disabled_attribute is not None and disabled_attribute.lower() == 'true'
    
    except TimeoutException:
        print("Button could not be found, treating as disabled.")
        return True

def seasonScrape(driver, finalLst, year):
    pageScrape(driver, finalLst, year)

    buttonDisabled = isButtonDisabled(driver, routes.buttons['nextPageButton'])
    while not buttonDisabled:
        try:
            nextPage(driver)
            pageScrape(driver, finalLst, year)
            buttonDisabled = isButtonDisabled(driver, routes.buttons['nextPageButton'])
        except StaleElementReferenceException as e:
            print(f"Encountered a stale element while moving to the next page for year {year}. Retrying... Error: {e}")
            time.sleep(1)  # Small delay before retrying

# def nextPage(driver):
#     try:
#         button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, routes.buttons['nextPageButton']))
#         )
#         button.click()
#     except TimeoutException:
#         print("Next page button could not be clicked.")


def nextPage(driver):
    try:
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, routes.buttons['nextPageButton']))
        )
        driver.execute_script("arguments[0].click();", button)
    except TimeoutException:
        print("Next page button could not be clicked.")


def mainScrape() -> list[list]:
    driver = webdriver.Firefox()
    driver.get(routes.mainLink)
    driver.maximize_window()

    print('Process has commenced'.center(40, '~'))

    finalLst = []
    currentYr = 2024

    seasonScrape(driver, finalLst, currentYr)
    currentYr -= 1

    dropdown = driver.find_element(By.XPATH, routes.buttons['selectDropDown'])
    select = Select(dropdown)

    for index in range(1, len(select.options)):
        select.select_by_index(index)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, routes.tableData['tableBody']))
        )

        seasonScrape(driver, finalLst, currentYr)
        print('Successfully scraped:', select.options[index].text)
        currentYr -= 1

    driver.quit()

    print(finalLst[:20])
    return finalLst

if __name__ == '__main__':
    mainScrape()
