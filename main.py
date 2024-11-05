import csv
from scraper import mainScrape
import time

def main():
    start = time.time()

    nbaData = mainScrape()
    csv_file = "1996-2024.csv"

    headers = [
        "YEAR", "PLAYER", "TEAM", "AGE", "GP", "W", "L", "MIN", 
        "DEF RTG", "DREB", "DREB%", "%DREB", "STL", "STL%", 
        "BLK", "%BLK", "OPP PTS OFF TOV", "OPP PTS 2ND CHANCE", 
        "OPP PTS FB", "OPP PTS PAINT", "DEF WS"
    ]

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:  # Specify encoding='utf-8'
        writer = csv.writer(file)

        writer.writerow(headers)

        for row in nbaData:
            writer.writerow(row)  # Write each row directly

    print('Data successfully written to', csv_file)

    end = time.time()
    timeMinutes = (end - start) / 60
    print('\nTime Taken:', timeMinutes)

if __name__ == '__main__':
    main()
