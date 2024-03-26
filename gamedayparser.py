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

# Define the Dropbox access token
dropbox_access_token = ("uat.AE00TcahKBhShtqopF6Qp-eMYIKrlGxLeM8FyCXyptJO0py_R-W3BxrDxhTeSudtZKVQkYW0X5Si77oNw3FjOpp-MjHhOWkwc88s8mf8SyesYkIZ3yfDGYTVj7FY_ErUcpa5dN_MuYghqx2LFTOvSWSUqedKPGppiVKspt9OZSbu5rJk7BYX6tv-wQB9M0iy7WmOOrwWDWE3BhEJTYC_aO7uvuzyz52fVfRhDntN-ehk9iDHJJmpcacYy66gppuf7Zszy1yJoB-fXcw44As9n9vCXKXeJTtLerf-0ZA3CMNKIc1fFRzlDnqs36AW5FPtdTjCgi6Gb_vuVrXGueau5SX4Y-59IazgPaMSC0G_cU643PQyfAZPRhuAaKT9njKiuEMmvOyY9Fal6XHzKRdQ5miEWKV4rYszsj2K3_eGEnSELrEle-p3RRe5OWK0AzYBfB0vf_Zu1VpmzFSp3ADXPyPE3D_4CQK6lOw7oTpSDu4KD4iF7nvBdNeYUYAMBbbQWS4ucAOWozRBX6oJ0joqWWI4-3OVA4roOakO0-onVYz3LCX-9Ckt8hoJeakslEIc00WyTodlBcP6MrMxdfZfQ6CQKzAKExR4o-Y08DqXYYMi18yS12Ubz2u5DuR1r7AKg84FG1YgocO24fQ4BJCvwN5Vr2232643FF0a5A6KW-m4TMDZPclgeC1LkLw9zUx9zyVQTpTXxICQtX5veuJv5LtvgeWpAEd7W1G2DO5237R0Dnlr_NmUo0WqIHbDFrCEv7XGsFHbuKI_2yngF7u8OyoxTH_SPXQ2W6CjicGnUAjb6hgWKk1yGF0MnRReJxWH3O3opbUxzNICE2pBPuG9XstrUu8wza2yWa5mMOykPVShEmENlAkrSEjN7_aBXDup8RB0yqrnJzPtp5GC7UeRtT04y6AkyDQIIKLDUobcAGFP6IQ9XJWhPNpuHivS0X0lCL7GKGrJy0J1BPp855Wlh46BauIJly9TSGzlpEGFQ9X4l-ECrP83DVtTK1ZWdS87pYscjKuEDPBLUgL9DeEAkj1xrH-shSRDq_eWHe7Zr28lBr_mWYHp2OeS83ZbixiZwN63EPQhEwPv-mIa9oEtdvDyPjbj0fPirhxXBauL039G5WTlKdvPVFcK-D7YqKlwcWJ-xOr_kGtBxQFuaCzQZOgu12EtCMr8e7aV7LLHu1IRcPDLR7jtNoQ-ysvAAW-XbgIndS-9fY5iqzhCOLIdJe9AXJ8waLKHH3f7fNS9OhtFUD-unBcCArf9smX7m4JN276k-zHkEJFoiVidRI6Uk4e1eGiumeCX78YkBRg6pFKprALoHV4EWgt1cnLGlKzJAsvuuFuEdtHvfXSgQjR6vvflJD58N_Vcy8OEAqyqx4HeVi6h51078nZ29iP8pi4eehKLj9oybdkf0AVOjPk48LJWfJiRv6kH5vMBFinm8-CJuQ")
adobe_client_secret = os.getenv("ADOBE_CLIENT_SECRET")
adobe_access_token = " "
adobe_api_key = os.getenv("ADOBE_API_KEY")

# Define API endpoints
urls = [
    "https://image.adobe.io/pie/psdService/text",
    "https://image.adobe.io/pie/psdService/actionJSON"
]

home_team_primary = [199, 81, 239]
home_team_secondary = [65, 37, 171]
away_team_primary = [250, 124, 88]
away_team_secondary = [143, 15, 211]



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
        self.record_home, self.seeding_home = self.get_record_and_seeding(self.home_team)
        self.record_away, self.seeding_away = self.get_record_and_seeding(self.away_team)
        self.last_5_games_results_home = self.get_last_5_games_results(self.home_team)
        self.last_5_games_results_away = self.get_last_5_games_results(self.away_team)

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
    def get_last_5_games_results(self, team_name):
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
    def get_record_and_seeding(self, team_name):
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

    # 1) Generate Adobe access token
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

    # 2) Generate a Dropbox download link from Gameday Generator/Base.psd and font
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

    # 3) Generate a Dropbox upload link from Gameday Generator/Base1.psd
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
    # 8) Read a file called actions_request.json and overwrite the file with the same things as request.json minus the things from the text editing part
    try:
        with open('C:\\Users\\ahmad\\OneDrive\\Gameday Generator\\actions_request.json', 'r') as file:
            data = json.load(file)

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
            if input_layer["href"] == "download_link":  # Check if href is "download_link"
                input_layer["href"] = download_link  # Assign the download_link value to href

        for output_layer in data["outputs"]:
            if output_layer["href"] == "upload_link":  # Check if href is "upload_link"
                output_layer["href"] = upload_link  # Assign the upload_link value to href

        for i in range(0, len(data["options"]["actionJSON"]), 2):
            select_action = data["options"]["actionJSON"][i]
            set_action = data["options"]["actionJSON"][i + 1]


        with open('C:\\Users\\ahmad\\OneDrive\\Gameday Generator\\NEW_actions_request.json', 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error modifying data: {e}")
        exit(1)

    # 9) Make a curl request using /psdService/actionJSON with all the previously allocated data
    action_curl_command = [
        'curl',
        '-X', 'POST',
        'https://image.adobe.io/pie/psdService/actionJSON',
        '--header', f'Authorization: Bearer {adobe_access_token}',
        '--header', f'x-api-key: {adobe_api_key}',
        '--header', 'Content-Type: application/json',
        '--data', json.dumps(data)  # Convert data to JSON string
    ]
    try:
        action_response = subprocess.check_output(action_curl_command)
        print("Action API Response:", action_response.decode())  # Print the output
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
    # 7) Generate ANOTHER Dropbox upload link from Gameday Generator/Base1.psd
    try:
        upload_output = subprocess.check_output(upload_curl_command)
        upload_output_json = json.loads(upload_output)
        upload_link = upload_output_json.get('link')
    except subprocess.CalledProcessError as e:
        print(f"Error generating upload link: {e}")
        exit(1)


    # 4) Read a file called text_request.json and overwrite the file with the same things as request.json, minus the things from actionJSON
    try:
        with open('C:\\Users\\ahmad\\OneDrive\\Gameday Generator\\text_request.json', 'r') as file:
            data = json.load(file)
        # Update the inputs and outputs fields
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
                input_layer["href"] = download_link  # Assign the text_download_link value to href
        for output_layer in data["outputs"]:
            if output_layer["href"] == "upload_link":  # Check if href is "upload_link"
                output_layer["href"] = upload_link  # Assign the text_upload_link value to href
        for font_layer in data["options"]["fonts"]:
            if font_layer["href"] == "font_link":  # Check if href is "font_download_link"
                font_layer["href"] = download_font_link  # Assign the text_download_link value to href

        with open('C:\\Users\\ahmad\\OneDrive\\Gameday Generator\\NEW_text_request.json', 'w') as file:
            json.dump(data, file, indent=4)
        
    except Exception as e:
        print(f"Error modifying data: {e}")
        exit(1)
        
  
    # 5) Make a curl request using /psdService/text with all the previously allocated data
    
    text_curl_command = [
        'curl',
        '-X', 'POST',
        'https://image.adobe.io/pie/psdService/text',
        '--header', f'Authorization: Bearer {adobe_access_token}',
        '--header', f'x-api-key: {adobe_api_key}',
        '--header', 'Content-Type: application/json',
        '--data', json.dumps(data)  # Convert data to JSON string
    ]
    try:
        text_response = subprocess.check_output(text_curl_command)
        print("Text API Response:", text_response.decode())  # Print the output
    except subprocess.CalledProcessError as e:
        print(f"Error executing cURL command for editing text: {e}")
    home_team_path = f'/team_logos/{team_crawler.home_team.lower().replace(" ", "")}.png'
    away_team_path = f'/team_logos/{team_crawler.away_team.lower().replace(" ", "")}.png'
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
    #download home and away team logos
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
    time.sleep(5)
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
     # 7) Generate ANOTHER Dropbox upload link from Gameday Generator/Base1.psd
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
        # Update the inputs and outputs fields            
        for layer in data["options"]["layers"]:
            if layer["name"] == "Home Team Logo":
                layer["input"]["href"] = download_home_link
            if layer["name"] == "Home Logo":
                layer["input"]["href"] = download_home_link
            if layer["name"] == "Away Team Logo":
                layer["input"]["href"] = download_away_link
            if layer["name"] == "Away Logo":
                layer["input"]["href"] = download_away_link
                
        for input_layer in data["inputs"]:
            if input_layer["href"] == "download_link":  # Check if href is "download_link"
                input_layer["href"] = download_link  # Assign the text_download_link value to href
        for output_layer in data["outputs"]:
            if output_layer["href"] == "upload_link":  # Check if href is "upload_link"
                output_layer["href"] = upload_link  # Assign the text_upload_link value to href
        
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
        '--data', json.dumps(data)  # Convert data to JSON string
    ]
    try:
        text_response = subprocess.check_output(image_curl_command)
        print("Image API Response:", text_response.decode())  # Print the output
    except subprocess.CalledProcessError as e:
        print(f"Error executing cURL command for editing text: {e}")


    

        
    

               

