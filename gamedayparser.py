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
        self.opponent = None
        # Initialize opponent attribute
        self.crawl(1, self.first_link)

    def setup_webdriver(self):
        try:
            options = Options()
            #Removes need to open webpage
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
            self.opponent = opponent_info[1].text.strip() if opponent_info else "N/A"
            formatted_date = self.format_date(raw_date)
            self.process_and_output_data(url, team_names, jerseys, location, formatted_date, time_data, self.opponent)

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

def get_last_5_games_results(team_name):
    base_url = f"https://www.statmuse.com/nba/ask/{team_name.lower().replace(' ', '-')}-last-5-games"
    response = requests.get(base_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract last 5 games results
        last_5_games = []

        game_result_divs = soup.find_all('div', {'class': 'w-5'})
        for div in game_result_divs:
            result = div.text.strip()
            last_5_games.append(result)

        return ''.join(last_5_games)
    else:
        print(f"Failed to fetch data from {base_url}")
        return None

def get_record_and_seeding(team_name):
    base_url = f"https://www.statmuse.com/ask/{team_name.lower().replace(' ', '-')}"
    response = requests.get(base_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract record and seeding
        record_element = soup.select_one('.whitespace-nowrap span:nth-of-type(1)')
        seeding_element = soup.select_one('.whitespace-nowrap span:nth-of-type(3)')

        record = record_element.text.strip() if record_element else "N/A"
        seeding = seeding_element.text.strip() if seeding_element else "N/A"

        return record, seeding
    else:
        print(f"Failed to fetch data from {base_url}")
        return None, None

if __name__ == "__main__":
    team_name = input("Enter the team name (e.g., Minnesota Timberwolves): ")

    team_crawler = WebCrawler(fr"https://lockervision.nba.com/team/{team_name.lower().replace(' ', '-')}", 1)
    
    record_home, seeding_home = get_record_and_seeding(team_name)
    if record_home and seeding_home:
        print(f"Home Record: {record_home}\nHome Seeding: {seeding_home}")
    else:
        print("Failed to fetch home record and seeding.")

    last_5_games_results_home = get_last_5_games_results(team_name)
    if last_5_games_results_home:
        print(f"Home Last 5 Games: {last_5_games_results_home}")
    else:
        print("Failed to fetch home last 5 games results.")
    
    record_away, seeding_away = get_record_and_seeding(team_crawler.opponent)
    if record_away and seeding_away:
        print(f"Away Record: {record_away}\nAway Seeding: {seeding_away}")
    else:
        print("Failed to fetch away record and seeding.")

    last_5_games_results_away = get_last_5_games_results(team_crawler.opponent)
    if last_5_games_results_away:
        print(f"Away Last 5 Games: {last_5_games_results_away}")
    else:
        print("Failed to fetch away last 5 games results.")
