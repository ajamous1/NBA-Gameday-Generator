#import libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
import requests
import json
import subprocess
from array import array
import os

# Define the Dropbox access token
dropbox_access_token = os.getenv("DROPBOX_ACCESS_TOKEN")
adobe_client_secret = os.getenv("ADOBE_CLIENT_SECRET")
adobe_access_token = os.getenv("ADOBE_ACCESS_TOKEN")
adobe_api_key = os.getenv("ADOBE_API_KEY")


#define API endpoints
urls = [
    "https://image.adobe.io/pie/psdService/actionJSON",
    "https://image.adobe.io/pie/psdService/text",
   
]

home_team_primary = [50, 20, 100]
home_team_secondary = [40, 70, 247]
away_team_primary = [30, 57, 70]
away_team_secondary = [20, 80, 40]

class WebCrawler:
    def __init__(self, link, num):
        print("WebCrawler created")
        self.first_link = link
        self.ID = num
        self.driver = self.setup_webdriver()
        self.home_team = None
        self.away_team = None
        self.record_home = None
        self.seeding_home = None
        self.record_away = None
        self.seeding_away = None
        self.last_5_games_results_home = None
        self.last_5_games_results_away = None
        self.raw_date = None
        self.time_data = None
        self.formatted_date = None
        self.crawl()


    def setup_webdriver(self):
        try:
            options = Options()
            options.add_argument('--headless')
            driver_path = r"C:\Users\ahmad\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
            return webdriver.Chrome(executable_path=driver_path, options=options)
        except WebDriverException as e:
            print(f"Error setting up Chromedriver: {e}")
            exit(1)
 
    def crawl(self):
        self.driver.get(self.first_link)
        time.sleep(2)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        team_names = soup.select_one('.MuiTypography-h5').text
        raw_date = soup.select_one('.MuiTypography-caption.MatchSeason').text
        location_elements = soup.select('h6.MuiTypography-h6')
        location_data = location_elements[1] if location_elements else None
        location = location_data.text.strip() if location_data else "N/A"
        self.time_data = soup.select_one('.MuiTypography-caption.MatchTime').text
        time_data = soup.select_one('.MuiTypography-caption.MatchTime').text
        jerseys_info = soup.select('.customEditionChip .MuiChip-label')
        jerseys = ', '.join([jersey.text for jersey in jerseys_info[:2]])
        opponent_info = soup.select('h5.MuiTypography-h5')
        self.away_team = opponent_info[1].text.strip() if opponent_info else "N/A"
        self.home_team = team_names.replace(self.away_team, "").strip()
        formatted_date = self.format_date(raw_date)
        self.formatted_date = formatted_date
        

        # Fetching additional data
        self.record_home, self.seeding_home = get_record_and_seeding(self.home_team)
        self.record_away, self.seeding_away = get_record_and_seeding(self.away_team)
        self.last_5_games_results_home = get_last_5_games_results(self.home_team)
        self.last_5_games_results_away = get_last_5_games_results(self.away_team)

        # Output data for both teams
        self.process_and_output_data(self.home_team, self.away_team, jerseys, location, formatted_date, time_data)

    def process_and_output_data(self, home_team, away_team, jerseys, location, date, time_data):
        try:
            print(f"Processed data:\nHome Team: {home_team}\nAway Team: {away_team} \nJerseys: {jerseys}\nLocation: {location}\nDate: {date}\nTime: {time_data}")
            print(f"Home Record: {self.record_home}\nHome Seeding: {self.seeding_home}")
            print(f"Home Last 5 Games: {self.last_5_games_results_home}")
            print(f"Away Record: {self.record_away}\nAway Seeding: {self.seeding_away}")
            print(f"Away Last 5 Games: {self.last_5_games_results_away}")
        except UnicodeEncodeError:
            print("UnicodeEncodeError: Unable to print some characters")

    def format_date(self, raw_date):
        return raw_date

    def quit_webdriver(self):
        self.driver.quit()

# Fetch last 5 games results
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

# Fetch team record and seeding
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
    team_name = input("Enter the team name: ")
    team_crawler = WebCrawler(fr"https://lockervision.nba.com/team/{team_name.lower().replace(' ', '-')}", 1)



# Define the curl command to generate Adobe access token
adobe_curl_command = [
    'curl',
    '-X', 'POST',
    'https://ims-na1.adobelogin.com/ims/token/v3',
    '-H', 'Content-Type: application/x-www-form-urlencoded',
    '-d', f'grant_type=client_credentials&client_id={adobe_api_key}&client_secret={adobe_client_secret}&scope=AdobeID,openid'
]

# Execute the curl command to generate Adobe access token
try:
    adobe_output = subprocess.check_output(adobe_curl_command)
    adobe_output_json = json.loads(adobe_output)
    adobe_access_token = adobe_output_json.get('access_token')
except subprocess.CalledProcessError as e:
    print(f"Error generating Adobe access token: {e}")
    exit(1)

# Print the generated Adobe access token
print("ADOBE ACCESS TOKEN:")
print(adobe_access_token)




# Define the curl command to generate download link
download_curl_command = [
    'curl',
    '-X', 'POST',
    'https://api.dropboxapi.com/2/files/get_temporary_link',
    '--header', f'Authorization: Bearer {dropbox_access_token}',
    '--header', 'Content-Type: application/json',
    '--data', '{"path":"/Gameday Generator/Base.psd"}'
]

# Execute the curl command to generate download link
try:
    download_output = subprocess.check_output(download_curl_command)
    download_output_json = json.loads(download_output)
    download_link = download_output_json.get('link')
except subprocess.CalledProcessError as e:
    print(f"Error generating download link: {e}")
    exit(1)

# Define the curl command to generate upload link
upload_curl_command = [
    'curl',
    '-X', 'POST',
    'https://api.dropboxapi.com/2/files/get_temporary_upload_link',
    '--header', f'Authorization: Bearer {dropbox_access_token}',
    '--header', 'Content-Type: application/json',
    '--data', '{"commit_info":{"path":"/Gameday Generator/Base1.psd","mode":{".tag":"overwrite"}}}'
]

# Execute the curl command to generate upload link
try:
    upload_output = subprocess.check_output(upload_curl_command)
    upload_output_json = json.loads(upload_output)
    upload_link = upload_output_json.get('link')
except subprocess.CalledProcessError as e:
    print(f"Error generating Adobe access token: {e}")
    exit(1)

# Print the generated Adobe access token
print("ADOBE ACCESS TOKEN:")
print(adobe_access_token)




# Define the curl command to generate download link
download_curl_command = [
    'curl',
    '-X', 'POST',
    'https://api.dropboxapi.com/2/files/get_temporary_link',
    '--header', f'Authorization: Bearer {dropbox_access_token}',
    '--header', 'Content-Type: application/json',
    '--data', '{"path":"/Gameday Generator/Base.psd"}'
]

# Execute the curl command to generate download link
try:
    download_output = subprocess.check_output(download_curl_command)
    download_output_json = json.loads(download_output)
    download_link = download_output_json.get('link')
except subprocess.CalledProcessError as e:
    print(f"Error generating download link: {e}")
    exit(1)

# Define the curl command to generate upload link
upload_curl_command = [
    'curl',
    '-X', 'POST',
    'https://api.dropboxapi.com/2/files/get_temporary_upload_link',
    '--header', f'Authorization: Bearer {dropbox_access_token}',
    '--header', 'Content-Type: application/json',
    '--data', '{"commit_info":{"path":"/Gameday Generator/Base1.psd","mode":{".tag":"overwrite"}}}'
]

# Execute the curl command to generate upload link
try:
    upload_output = subprocess.check_output(upload_curl_command)
    upload_output_json = json.loads(upload_output)
    upload_link = upload_output_json.get('link')
except subprocess.CalledProcessError as e:
    print(f"Error generating upload link: {e}")
    exit(1)

# Print the generated links
print("DOWNLOAD LINK:")
print(download_link)
print("UPLOAD LINK:")
print(upload_link)


# Load the JSON file
try:
     with open('C:\\Users\\ahmad\\OneDrive\\Gameday Generator\\request.json', 'r') as file:
        data = json.load(file)
except Exception as e:
    print(f"Error loading JSON file: {e}")
    exit(1)

# Modify the data according to the crawled values
try:
  for layer in data["options"]["layers"]:
    if layer["name"] == "Away Position":
        layer["text"]["contents"] = team_crawler.seeding_away
    if layer["name"] == "Home Position":
        layer["text"]["contents"] = team_crawler.seeding_home
    if layer["name"] == "Away Record":
        layer["text"]["contents"] = team_crawler.record_away
    if layer["name"] == "Home Record":
        layer["text"]["contents"] = team_crawler.record_home
    if layer["name"] == "Away Team":
        layer["text"]["contents"] = team_crawler.away_team
    if layer["name"] == "Home Team":
        layer["text"]["contents"] = team_crawler.home_team
    if layer["name"] == "Date":
        layer["text"]["contents"] = team_crawler.formatted_date
    if layer["name"] == "Time":
        layer["text"]["contents"] = team_crawler.time_data

  for input_layer in data["inputs"]:
    if input_layer["href"] == "download_link":  # Check if href is "download_link"
        input_layer["href"] = download_link  # Assign the download_link value to href

  for output_layer in data["outputs"]:
    if output_layer["href"] == "upload_link":  # Check if href is "upload_link"
        output_layer["href"] = upload_link  # Assign the upload_link value to href
  for i in range(0, len(data["options"]["actionJSON"]), 2):
    select_action = data["options"]["actionJSON"][i]
    set_action = data["options"]["actionJSON"][i+1]
    
    # Get the layer name from the select action
    layer_name = select_action["_target"][0]["_name"]
    
    # Update the color values in the set action based on the layer name
    if layer_name == "Home Team Primary":
        set_action["to"]["color"]["red"] = home_team_primary[0]
        set_action["to"]["color"]["grain"] = home_team_primary[1]
        set_action["to"]["color"]["blue"] = home_team_primary[2]
    if layer_name == "Home Team Secondary":
        set_action["to"]["color"]["red"] = home_team_secondary[0]
        set_action["to"]["color"]["grain"] = home_team_secondary[1]
        set_action["to"]["color"]["blue"] = home_team_secondary[2]
    if layer_name == "Away Team Primary":
        set_action["to"]["color"]["red"] = away_team_primary[0]
        set_action["to"]["color"]["grain"] = away_team_primary[1]
        set_action["to"]["color"]["blue"] = away_team_primary[2]
    if layer_name == "Away Team Secondary":
        set_action["to"]["color"]["red"] = away_team_secondary[0]
        set_action["to"]["color"]["grain"] = away_team_secondary[1]
        set_action["to"]["color"]["blue"] = away_team_secondary[2]

    
    # Iterate over the actions in 'actionJSON'
  for i in range(len(data["options"]["actionJSON"])):
    if data["options"]["actionJSON"][i]["_obj"] == "select":
        layer_name = data["options"]["actionJSON"][i]["_target"][0]["_name"]
    elif data["options"]["actionJSON"][i]["_obj"] == "set":
        if "to" in data["options"]["actionJSON"][i] and "gradient" in data["options"]["actionJSON"][i]["to"]:
            if layer_name == "Home Team Gradient":
                for color_stop in data["options"]["actionJSON"][i]["to"]["gradient"]["colors"]:
                    color_stop["color"]["red"] = home_team_secondary[0]
                    color_stop["color"]["grain"] = home_team_secondary[1]
                    color_stop["color"]["blue"] = home_team_secondary[2]
            if layer_name == "Away Team Gradient":
                for color_stop in data["options"]["actionJSON"][i]["to"]["gradient"]["colors"]:
                    color_stop["color"]["red"] = away_team_secondary[0]
                    color_stop["color"]["grain"] = away_team_secondary[1]
                    color_stop["color"]["blue"] = away_team_secondary[2]

        
except Exception as e:
    print(f"Error modifying data: {e}")
    exit(1)

# Write the modified data back to the NEW JSON file
try:
    with open('C:\\Users\\ahmad\\OneDrive\\Gameday Generator\\NEWrequest.json', 'w') as file:
        json.dump(data, file, indent=4)
except Exception as e:
    print(f"Error writing to NEW JSON file: {e}")
    exit(1)

# Define the curl command with the corrected file path
curl_command = [
    'curl',
    '-X', 'POST',
    *urls,
    '-H', f'Authorization: Bearer {adobe_access_token}',
    '-H', f'x-api-key: {adobe_api_key}',
    '-H', 'Content-Type: application/json',
    '-d', f'@C:\\Users\\ahmad\\OneDrive\\Gameday Generator\\NEWrequest.json'  # Use double backslashes for the file path
]

# Execute the curl command
try:
    output = subprocess.check_output(curl_command)
    print(output.decode('utf-8'))
except subprocess.CalledProcessError as e:
    print(f"Error executing curl command: {e}")


