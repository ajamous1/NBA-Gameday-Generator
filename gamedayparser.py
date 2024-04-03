#import libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
import requests
import json
import subprocess
import os
import pytz
from datetime import datetime, timedelta

dropbox_access_token = ("uat.AE6RgUUUnXn4HDUpY5ylsjvVEBu_gVR1SK2XX0ukxjf9BurTGWmyv9EJFGlYWZsDKYQuSivPkV69eHARVXgfOv-9JGJIQWyDLRY5FJfqIWUWnWidxZAB1q-R3FbKIpqEe7Kfxdbekxm3tw0MTHAhOLB5UyYWrJVt6ed9sy8yBUhjp6umCQ2JtACR8kfCIAPZAKZFhKSKsNIXQGctd3-qt_nHgJgAKQvWi9xWoi0ceX9Kgjcz6vNI5prRJZS8PAKh54BLVtnXhJ06QhAF5ADab2KYqgpj4NM70_dswrwsmvAW6QzEQUXOgrdvtqb76mQcwqmqwf7q4dk_p8bL_aPQJaEvtXgMzNJUKfmTZ0NvOzJwQQIJhFX6XslmOcjM3cJrzLK0IMPJC_1IroIn_7eMZXDnPc3_NK6sRZUDMou3rwKoFHDeAoHnoLR4bCj-lQIdmbzXn51dl9SML7S0ANCe8Cy4-UsYpEgYGnXTvbLsfGkbNLUuFyRCCUVGhazZFxG1L8lf0VqmbSTHTFqNavVMjDYNUavDU2JG9gkQDwsqgdH9p37HkmsSokkUttldlC_lsaZqX04apRJ6Pc_DmcU2dJ1I57je5Mn3oZo1KL1I08o6olhYz30sxC1vy5GhQolJgsR2k_mHjK-H8s5n3RL2ksRDm-NIgpXxvhn7rDOYLYTCNO93ra8C6QcvUrHNwLaxKjoB8secoAEjmrNCsKdRG9Ztj92-GuG_a7lokp_ZSfGwsq2l9i5Z4_P0BZuC07jeL7rTNDSVy2psgq8OMZFff_nhu-YfoSWB1e7YBJSb8VsE-GgBrD--oOwDljk2pAGOKVEr_M4kTOS5Wk8bteigcLfSTZBBkdatl2Tv25hqkX17EQusUYUYfmaUsOIv7RgUvDkcf5C9ahmbBXt0GiB7L3s0Lr1uvQa6IUgVKubMoC1nVAOnOHsIwDL8Y0QuKw7mfdls5-WbQtCUG-Iet_fAnPt2I36sj_drudf13OHFYvUcYMq3auW4uMR7-m8wU6Jai4brmRo6lVXBqRlKEdbPldbKYrFRpvETrtySOL0g06Lp9ZnMGo1DiYTw_mWw_WHwyWdRx84SskonWAd2UU5jhJRzr7t3Ph8kWLZa2kjrZ4JmIsL6w_AsrVys24p8jGRFmp-h5GKFZi81GZ-xVAdo_9aaIkZf8Lj1QvPPmlegdxXILDaCZI0KA_ymhAcC1rcNyvYL_1I9mOlLXPjI5JoLP5h5S7KgFJAj3uUndX2L0deelKstxvJBDtK3EOoeQoKvyMH8NlGj4QcEeGX52Kf_yuO-hLoBW4t7a70N4yU-t_yF4OVip6HbPMhvouoiAgHE860sPXKQsDrRbP6lqGDT4a9po6RYUfLGXqBCdJKEFKOr7o1zHIC8HvBQzYH6TiHZL7gIK0u0Bo0qnypbFA7eAKHN9NIfLeLzYeDlbtI4TA982Q")
adobe_client_secret = os.getenv("ADOBE_CLIENT_SECRET")
adobe_access_token = " "
adobe_api_key = os.getenv("ADOBE_API_KEY")




home_team_primary = [0, 0, 0]
home_team_secondary = [0, 0, 0]
away_team_primary = [0, 0, 0]
away_team_secondary = [0, 0, 0]



class WebCrawler:
    def __init__(self, first_link, num):
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
        self.first_link = first_link
        self.crawl()

    def setup_webdriver(self):
        try:
            options = Options()
            options.add_argument('--headless')
            driver_path = r'C:\Users\ahmad\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'
            return webdriver.Chrome(executable_path=driver_path, options=options)
        except WebDriverException as e:
            print(f"Error setting up Chromedriver: {e}")
            exit(1)
 
    def crawl(self):
        global home_team_primary, home_team_secondary, away_team_primary, away_team_secondary
        

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
        formatted_time = self.format_time(self.time_data)
        self.formatted_time = formatted_time
        jerseys_info = soup.select('.customEditionChip .MuiChip-label')
        jerseys = ', '.join([jersey.text for jersey in jerseys_info[:2]])
        opponent_info = soup.select('h5.MuiTypography-h5')
        self.away_team = opponent_info[1].text.strip() if opponent_info else "N/A"
        self.home_team = team_names.replace(self.away_team, "").strip()
        formatted_date = self.format_date(raw_date)
        self.formatted_date = formatted_date
        global home_jersey, away_jersey
        home_jersey, away_jersey = jerseys.split(', ')
        self.record_home, self.seeding_home = self.get_record_and_seeding(self.home_team)
        self.record_away, self.seeding_away = self.get_record_and_seeding(self.away_team)
        self.last_5_games_results_home = self.get_last_5_games_results(self.home_team)
        self.last_5_games_results_away = self.get_last_5_games_results(self.away_team)

        with open(r"C:\Users\ahmad\NBA-Gameday-Generator\nba_colors.json", 'r') as f:
            nba_colors = json.load(f)

      
        home_team_primary = nba_colors[self.home_team.title()][home_jersey]["first_color"]
        home_team_secondary = nba_colors[self.home_team.title()][home_jersey]["second_color"]
        away_team_primary = nba_colors[self.away_team.title()][away_jersey]["first_color"]
        away_team_secondary = nba_colors[self.away_team.title()][away_jersey]["second_color"]
  


        
       

     
        

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
        formatted_date = raw_date.split(', ')[1]
        return formatted_date

    
    def format_time(self, raw_time):
       
        raw_time = " ".join(raw_time.split())
       
        time, am_pm, timezone = raw_time.split()
        
        time_object = datetime.strptime(time + ' ' + am_pm, '%I:%M %p')
      
        if timezone == 'EST':
            time_object = time_object - timedelta(hours=1)  # Convert EST to CST
    
        formatted_time = time_object.strftime('%I:%M %p\nCT').lstrip('0')
        return formatted_time

    def quit_webdriver(self):
        self.driver.quit()

   
    def get_last_5_games_results(self, team_name):
        base_url = f"https://www.statmuse.com/nba/ask/{team_name.lower().replace(' ', '-')}-last-5-games"
        response = requests.get(base_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            
            last_5_games = []

            game_result_divs = soup.find_all('div', {'class': 'w-5'})
            for div in game_result_divs:
                result = div.text.strip()
                last_5_games.append(result)

            return ''.join(last_5_games)
        else:
            print(f"Failed to fetch data from {base_url}")
            return None

   
    def get_record_and_seeding(self, team_name):
        base_url = f"https://www.statmuse.com/ask/{team_name.lower().replace(' ', '-')}"
        response = requests.get(base_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            
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

    
    adobe_curl_command = [
        'curl',
        '-X', 'POST',
        'https://ims-na1.adobelogin.com/ims/token/v3',
        '-H', 'Content-Type: application/x-www-form-urlencoded',
        '-d', f'grant_type=client_credentials&client_id={adobe_api_key}&client_secret={adobe_client_secret}&scope=AdobeID,openid'
    ]
    try:
        adobe_output = subprocess.check_output(adobe_curl_command)
        adobe_output_json = json.loads(adobe_output)
        adobe_access_token = adobe_output_json.get('access_token')
    except subprocess.CalledProcessError as e:
        print(f"Error generating Adobe access token: {e}")
        exit(1)

   
    download_curl_command = [
        'curl',
        '-X', 'POST',
        'https://api.dropboxapi.com/2/files/get_temporary_link',
        '--header', f'Authorization: Bearer {dropbox_access_token}',
        '--header', 'Content-Type: application/json',
        '--data', '{"path":"/Gameday Generator/Base1.psd"}'
    ]
    try:
        download_output = subprocess.check_output(download_curl_command)
        download_output_json = json.loads(download_output)
        download_link = download_output_json.get('link')
    except subprocess.CalledProcessError as e:
        print(f"Error generating download link: {e}")
        exit(1)

    download_font_curl_command = [
        'curl',
        '-X', 'POST',
        'https://api.dropboxapi.com/2/files/get_temporary_link',
        '--header', f'Authorization: Bearer {dropbox_access_token}',
        '--header', 'Content-Type: application/json',
        '--data', '{"path":"/Lovelo/Lovelo-Black.ttf"}'
    ]
    try:
        download_output = subprocess.check_output(download_font_curl_command)
        download_output_json = json.loads(download_output)
        download_font_link = download_output_json.get('link')
    except subprocess.CalledProcessError as e:
        print(f"Error generating download link: {e}")
        exit(1)

    
    upload_curl_command = [
        'curl',
        '-X', 'POST',
        'https://api.dropboxapi.com/2/files/get_temporary_upload_link',
        '--header', f'Authorization: Bearer {dropbox_access_token}',
        '--header', 'Content-Type: application/json',
        '--data', '{"commit_info":{"path":"/Gameday Generator/Base1.psd","mode":{".tag":"overwrite"}}}'
    ]
    try:
        upload_output = subprocess.check_output(upload_curl_command)
        upload_output_json = json.loads(upload_output)
        upload_link = upload_output_json.get('link')
    except subprocess.CalledProcessError as e:
        print(f"Error generating upload link: {e}")
        exit(1)
   
    team_crawler.last_5_games_results_home = list(team_crawler.last_5_games_results_home)
    team_crawler.last_5_games_results_away = list(team_crawler.last_5_games_results_away)
    try:
        with open('C:\\Users\\ahmad\\OneDrive\\Gameday Generator\\actions_request.json', 'r') as file:
            data = json.load(file)
             
   
      
        layer_name = None 
        for i in range(0, len(data["options"]["actionJSON"]), 2):
            select_action = data["options"]["actionJSON"][i]
            set_action = data["options"]["actionJSON"][i+1]
                    
            
            layer_name = select_action["_target"][0]["_name"]
    

          
            if layer_name == "W/L (1) Home" and team_crawler.last_5_games_results_home[0] != "L":
                        set_action["to"]["color"]["red"] = home_team_primary[0]
                        set_action["to"]["color"]["grain"] = home_team_primary[1]
                        set_action["to"]["color"]["blue"] = home_team_primary[2]
            if layer_name == "W/L (2) Home" and team_crawler.last_5_games_results_home[1] != "L":
                        set_action["to"]["color"]["red"] = home_team_primary[0]
                        set_action["to"]["color"]["grain"] = home_team_primary[1]
                        set_action["to"]["color"]["blue"] = home_team_primary[2]
            if layer_name == "W/L (3) Home" and team_crawler.last_5_games_results_home[2] != "L":
                        set_action["to"]["color"]["red"] = home_team_primary[0]
                        set_action["to"]["color"]["grain"] = home_team_primary[1]
                        set_action["to"]["color"]["blue"] = home_team_primary[2]
            if layer_name == "W/L (4) Home" and team_crawler.last_5_games_results_home[3] != "L":
                        set_action["to"]["color"]["red"] = home_team_primary[0]
                        set_action["to"]["color"]["grain"] = home_team_primary[1]
                        set_action["to"]["color"]["blue"] = home_team_primary[2]
            if layer_name == "W/L (5) Home" and team_crawler.last_5_games_results_home[4] != "L":
                        set_action["to"]["color"]["red"] = home_team_primary[0]
                        set_action["to"]["color"]["grain"] = home_team_primary[1]
                        set_action["to"]["color"]["blue"] = home_team_primary[2]
            if layer_name == "W/L (1) Away" and team_crawler.last_5_games_results_away[0] != "L":
                        set_action["to"]["color"]["red"] = away_team_primary[0]
                        set_action["to"]["color"]["grain"] = away_team_primary[1]
                        set_action["to"]["color"]["blue"] = away_team_primary[2]
            if layer_name == "W/L (2) Away" and team_crawler.last_5_games_results_away[1] != "L":
                        set_action["to"]["color"]["red"] = away_team_primary[0]
                        set_action["to"]["color"]["grain"] = away_team_primary[1]
                        set_action["to"]["color"]["blue"] = away_team_primary[2]
            if layer_name == "W/L (3) Away" and team_crawler.last_5_games_results_away[2] != "L":
                        set_action["to"]["color"]["red"] = away_team_primary[0]
                        set_action["to"]["color"]["grain"] = away_team_primary[1]
                        set_action["to"]["color"]["blue"] = away_team_primary[2]
            if layer_name == "W/L (4) Away" and team_crawler.last_5_games_results_away[3] != "L":
                        set_action["to"]["color"]["red"] = away_team_primary[0]
                        set_action["to"]["color"]["grain"] = away_team_primary[1]
                        set_action["to"]["color"]["blue"] = away_team_primary[2]
            if layer_name == "W/L (5) Away" and team_crawler.last_5_games_results_away[4] != "L":
                        set_action["to"]["color"]["red"] = away_team_primary[0]
                        set_action["to"]["color"]["grain"] = away_team_primary[1]
                        set_action["to"]["color"]["blue"] = away_team_primary[2]
                
                            
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
        for input_layer in data["inputs"]:
            if input_layer["href"] == "download_link": 
                input_layer["href"] = download_link  

        for output_layer in data["outputs"]:
            if output_layer["href"] == "upload_link":
                output_layer["href"] = upload_link 

        for i in range(0, len(data["options"]["actionJSON"]), 2):
            select_action = data["options"]["actionJSON"][i]
            set_action = data["options"]["actionJSON"][i + 1]


        with open('C:\\Users\\ahmad\\OneDrive\\Gameday Generator\\NEW_actions_request.json', 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error modifying data: {e}")
        exit(1)

    
    action_curl_command = [
        'curl',
        '-X', 'POST',
        'https://image.adobe.io/pie/psdService/actionJSON',
        '--header', f'Authorization: Bearer {adobe_access_token}',
        '--header', f'x-api-key: {adobe_api_key}',
        '--header', 'Content-Type: application/json',
        '--data', json.dumps(data) 
    ]
    try:
        action_response = subprocess.check_output(action_curl_command)
        print("Action API Response:", action_response.decode()) 
    except subprocess.CalledProcessError as e:
        print(f"Error executing cURL command for performing actions on JSON data: {e}")


    time.sleep(5)
    download_curl_command = [
        'curl',
        '-X', 'POST',
        'https://api.dropboxapi.com/2/files/get_temporary_link',
        '--header', f'Authorization: Bearer {dropbox_access_token}',
        '--header', 'Content-Type: application/json',
        '--data', '{"path":"/Gameday Generator/Base1.psd"}'
    ]
    try:
        download_output = subprocess.check_output(download_curl_command)
        download_output_json = json.loads(download_output)
        download_link = download_output_json.get('link')
    except subprocess.CalledProcessError as e:
        print(f"Error generating download link: {e}")
        exit(1)
 
    try:
        upload_output = subprocess.check_output(upload_curl_command)
        upload_output_json = json.loads(upload_output)
        upload_link = upload_output_json.get('link')
    except subprocess.CalledProcessError as e:
        print(f"Error generating upload link: {e}")
        exit(1)


 

    

   




    try:
        with open('C:\\Users\\ahmad\\OneDrive\\Gameday Generator\\text_request.json', 'r') as file:
            data = json.load(file)
        
        for layer in data["options"]["layers"]:
            for i in range(1, 6): 
                if layer["name"] == f"Game {i} Home":
                    layer["text"]["contents"] = team_crawler.last_5_games_results_home[i-1]
                if layer["name"] == f"Game {i} Away":
                    layer["text"]["contents"] = team_crawler.last_5_games_results_away[i-1]
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
                layer["text"]["contents"] = team_crawler.formatted_time
        for input_layer in data["inputs"]:
            if input_layer["href"] == "download_link":  
                input_layer["href"] = download_link
        for output_layer in data["outputs"]:
            if output_layer["href"] == "upload_link":  
                output_layer["href"] = upload_link  
        for font_layer in data["options"]["fonts"]:
            if font_layer["href"] == "font_link": 
                font_layer["href"] = download_font_link  
        with open('C:\\Users\\ahmad\\OneDrive\\Gameday Generator\\NEW_text_request.json', 'w') as file:
            json.dump(data, file, indent=4)
        
    except Exception as e:
        print(f"Error modifying data: {e}")
        exit(1)
        
  
   
    text_curl_command = [
        'curl',
        '-X', 'POST',
        'https://image.adobe.io/pie/psdService/text',
        '--header', f'Authorization: Bearer {adobe_access_token}',
        '--header', f'x-api-key: {adobe_api_key}',
        '--header', 'Content-Type: application/json',
        '--data', json.dumps(data) 
    ]
    try:
        text_response = subprocess.check_output(text_curl_command)
        print("Text API Response:", text_response.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error executing cURL command for editing text: {e}")
    if home_jersey == "Association Edition" or home_jersey == "Icon Edition":
        home_jersey = "Default"
        
    if away_jersey == "Association Edition" or away_jersey == "Icon Edition":
        away_jersey = "Default"
      
    home_team_path = f'/team_logos/{home_jersey}/{team_crawler.home_team.lower().replace(" ", "")}.png'
    away_team_path = f'/team_logos/{away_jersey}/{team_crawler.away_team.lower().replace(" ", "")}.png'
    arena_path = f'/arenas/{team_crawler.home_team.lower().replace(" ", "")}.png'
    
    time.sleep(10)
    download_curl_command = [
        'curl',
        '-X', 'POST',
        'https://api.dropboxapi.com/2/files/get_temporary_link',
        '--header', f'Authorization: Bearer {dropbox_access_token}',
        '--header', 'Content-Type: application/json',
        '--data', '{"path":"/Gameday Generator/Base1.psd"}'
    ]
    try:
        download_output = subprocess.check_output(download_curl_command)
        download_output_json = json.loads(download_output)
        download_link = download_output_json.get('link')
    except subprocess.CalledProcessError as e:
        print(f"Error generating download link: {e}")
        exit(1)
    
    download_home_curl_command = [
        'curl',
        '-X', 'POST',
        'https://api.dropboxapi.com/2/files/get_temporary_link',
        '--header', f'Authorization: Bearer {dropbox_access_token}',
        '--header', 'Content-Type: application/json',
        '--data', f'{{"path":"{home_team_path}"}}'
    ]

    try:
    
        download_output = subprocess.check_output(download_home_curl_command)

        download_output_json = json.loads(download_output)
        download_home_link = download_output_json.get('link')
    except subprocess.CalledProcessError as e:
        print(f"Error generating download link: {e}")
        exit(1)
 
    download_away_curl_command = [
        'curl',
        '-X', 'POST',
        'https://api.dropboxapi.com/2/files/get_temporary_link',
        '--header', f'Authorization: Bearer {dropbox_access_token}',
        '--header', 'Content-Type: application/json',
        '--data', f'{{"path":"{away_team_path}"}}'
    ]

    try:
        download_output = subprocess.check_output(download_away_curl_command)
        download_output_json = json.loads(download_output)
        download_away_link = download_output_json.get('link')
    
    except subprocess.CalledProcessError as e:
        print(f"Error generating download link: {e}")
        exit(1)

    download_arena_curl_command = [
        'curl',
        '-X', 'POST',
        'https://api.dropboxapi.com/2/files/get_temporary_link',
        '--header', f'Authorization: Bearer {dropbox_access_token}',
        '--header', 'Content-Type: application/json',
        '--data', f'{{"path":"{arena_path}"}}'
    ]
    try:
        download_output = subprocess.check_output(download_arena_curl_command)
        download_output_json = json.loads(download_output)
        download_arena_link = download_output_json.get('link')
    except subprocess.CalledProcessError as e:
        print(f"Error generating download link: {e}")
        exit(1)
    
    try:
        upload_output = subprocess.check_output(upload_curl_command)
        upload_output_json = json.loads(upload_output)
        upload_link = upload_output_json.get('link')
    except subprocess.CalledProcessError as e:
        print(f"Error generating upload link: {e}")
        exit(1)
    try:
        with open('C:\\Users\\ahmad\\OneDrive\\Gameday Generator\\image_request.json', 'r') as file:
            data = json.load(file)
              
        for layer in data["options"]["layers"]:
            if layer["name"] == "Home Team Logo":
                layer["input"]["href"] = download_home_link
            if layer["name"] == "Home Logo":
                layer["input"]["href"] = download_home_link
            if layer["name"] == "Away Team Logo":
                layer["input"]["href"] = download_away_link
            if layer["name"] == "Away Logo":
                layer["input"]["href"] = download_away_link
            if layer["name"] == "Arena Logo":
                layer["input"]["href"] = download_arena_link

                
        for input_layer in data["inputs"]:
            if input_layer["href"] == "download_link": 
                input_layer["href"] = download_link  
        for output_layer in data["outputs"]:
            if output_layer["href"] == "upload_link": 
                output_layer["href"] = upload_link 
        
        with open('C:\\Users\\ahmad\\OneDrive\\Gameday Generator\\NEW_image_request.json', 'w') as file:
            json.dump(data, file, indent=4)
        
    except Exception as e:
        print(f"Error modifying data: {e}")
        exit(1)
    image_curl_command = [
        'curl',
        '-X', 'POST',
        'https://image.adobe.io/pie/psdService/smartObject',
        '--header', f'Authorization: Bearer {adobe_access_token}',
        '--header', f'x-api-key: {adobe_api_key}',
        '--header', 'Content-Type: application/json',
        '--data', json.dumps(data)  
    ]
    try:
        text_response = subprocess.check_output(image_curl_command)
        print("Image API Response:", text_response.decode()) 
    except subprocess.CalledProcessError as e:
        print(f"Error executing cURL command for editing text: {e}")


    

        
    

               
