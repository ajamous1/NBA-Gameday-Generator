from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
import requests

class WebCrawler:
    def __init__(self, link, num):
        print("WebCrawler created")
        self.first_link = link
        self.ID = num
        self.driver = self.setup_webdriver()
        self.crawl(1, self.first_link)

    def setup_webdriver(self):
        try:
            options = Options()
            options.add_argument('--headless')
            driver_path = r'C:\Users\ahmad\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'
            return webdriver.Chrome(executable_path=driver_path, options=options)
        except WebDriverException as e:
            print(f"Error setting up Chromedriver: {e}")
            exit(1)

    def crawl(self, level, url):
        if level <= 1:
            self.driver.get(url)
            time.sleep(2)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            team_names = soup.select_one('.MuiTypography-h5').text
            raw_date = soup.select_one('.MuiTypography-caption.MatchSeason').text
            location_elements = soup.select('h6.MuiTypography-h6')
            location_data = location_elements[1] if location_elements else None
            location = location_data.text.strip() if location_data else "N/A"
            time_data = soup.select_one('.MuiTypography-caption.MatchTime').text
            jerseys_info = soup.select('.customEditionChip .MuiChip-label')
            jerseys = ', '.join([jersey.text for jersey in jerseys_info[:2]])
            opponent_info = soup.select('h5.MuiTypography-h5')
            opponent = opponent_info[1].text.strip() if opponent_info else "N/A"
            formatted_date = self.format_date(raw_date)
            self.process_and_output_data(url, team_names, jerseys, location, formatted_date, time_data, opponent)

    def process_and_output_data(self, url, team_names, jerseys, location, date, time_data, opponent):
        try:
            print(f"Processed data from {url}:\nHome Team: {team_names}\nAway Team: {opponent} \nJerseys: {jerseys}\nLocation: {location}\nDate: {date}\nTime: {time_data}")
        except UnicodeEncodeError:
            print("UnicodeEncodeError: Unable to print some characters")

    def format_date(self, raw_date):
        return raw_date

    def quit_webdriver(self):
        self.driver.quit()

def parse_record(record_text):
    # Extracting the record
    record = record_text.find('strong').next_sibling.strip().split(',')[0]
    return record

def get_last_5_games_results(team_code, year):
    base_url = f"https://www.basketball-reference.com/teams/{team_code}/{year}/gamelog/"
    response = requests.get(base_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract last 5 games results
        last_5_games = []

        game_log_table = soup.find('table', {'id': 'tgl_basic'})
        if game_log_table:
            rows = game_log_table.find_all('tr', {'class': 'full_table'})

            # Find the largest 'tgl_basic' value
            max_tgl_basic = max(int(row['id'].split('.')[-1]) for row in rows if 'tgl_basic' in row['id']) if rows else 0

            # Collect results for the last 5 games
            for i in range(max_tgl_basic, max_tgl_basic - 5, -1):
                result_row = soup.find('tr', {'id': f'tgl_basic.{i}'})
                if result_row:
                    result = result_row.find('td', {'data-stat': 'game_result'}).text.strip()
                    last_5_games.append(result)

        return last_5_games[::-1]  
    else:
        print(f"Failed to fetch data from {base_url}")
        return None

if __name__ == "__main__":
    team1 = input("Enter the first team: ").replace(' ', '-').lower()
    team_crawler = WebCrawler(fr"https://lockervision.nba.com/team/{team1}", 1)

    team_code = input("Enter the team code (e.g., MIN): ").upper()
    year = input("Enter the year (e.g., 2024): ")

    record_html = """
    <p>
        <strong>Record:</strong>

          30-11, 1st in <a href="/leagues/NBA_2024.html">NBA</a> 
         Western Conference    

    </p>
    """
    record_text = parse_record(BeautifulSoup(record_html, 'html.parser'))
    print(f"Record: {record_text}")

    last_5_games_results = get_last_5_games_results(team_code, year)
    if last_5_games_results:
        print(f"Last 5 Games Results: {last_5_games_results}")
    else:
        print("Failed to fetch last 5 games results.")
