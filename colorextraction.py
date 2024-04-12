from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from PIL import Image
from PIL import ImageEnhance
import numpy as np
import requests
import os
import json
import time

nba_teams = {
    "Atlanta Hawks": {"Color 1": [225, 68, 52], "Color 2": [253, 185, 39]},
    "Boston Celtics": {"Color 1": [0, 122, 51], "Color 2": [139, 111, 78]},
    "Brooklyn Nets": {"Color 1": [0, 0, 0], "Color 2": [255, 255, 255]},
    "Charlotte Hornets": {"Color 1": [29, 17, 96], "Color 2": [0, 120, 140]},
    "Chicago Bulls": {"Color 1": [206, 17, 65], "Color 2": [6, 25, 34]},
    "Cleveland Cavaliers": {"Color 1": [134, 0, 56], "Color 2": [4, 30, 66]},
    "Dallas Mavericks": {"Color 1": [0, 83, 188], "Color 2": [0, 43, 92]},
    "Denver Nuggets": {"Color 1": [13, 34, 64], "Color 2": [255, 198, 39]},
    "Detroit Pistons": {"Color 1": [200, 16, 46], "Color 2": [29, 66, 138]},
    "Golden State Warriors": {"Color 1": [29, 66, 138], "Color 2": [255, 199, 44]},
    "Houston Rockets": {"Color 1": [206, 17, 65], "Color 2": [6, 25, 34]},
    "Indiana Pacers": {"Color 1": [0, 45, 98], "Color 2": [253, 187, 48]},
    "La Clippers": {"Color 1": [200, 16, 46], "Color 2": [29, 66, 148]},
    "Los Angeles Lakers": {"Color 1": [85, 37, 130], "Color 2": [253, 185, 39]},
    "Memphis Grizzlies": {"Color 1": [93, 118, 169], "Color 2": [18, 23, 63]},
    "Miami Heat": {"Color 1": [152, 0, 46], "Color 2": [249, 160, 27]},
    "Milwaukee Bucks": {"Color 1": [0, 71, 27], "Color 2": [240, 235, 210]},
    "Minnesota Timberwolves": {"Color 1": [12, 35, 64], "Color 2": [35, 97, 146]},
    "New Orleans Pelicans": {"Color 1": [0, 22, 65], "Color 2": [225, 58, 62]},
    "New York Knicks": {"Color 1": [0, 107, 182], "Color 2": [245, 132, 38]},
    "Oklahoma City Thunder": {"Color 1": [0, 125, 195], "Color 2": [239, 59, 36]},
    "Orlando Magic": {"Color 1": [0, 125, 197], "Color 2": [196, 206, 211]},
    "Philadelphia 76Ers": {"Color 1": [0, 107, 182], "Color 2": [237, 23, 76]},
    "Phoenix Suns": {"Color 1": [29, 17, 96], "Color 2": [229, 95, 32]},
    "Portland Trail Blazers": {"Color 1": [224, 58, 62], "Color 2": [6, 25, 34]},
    "Sacramento Kings": {"Color 1": [91, 43, 130], "Color 2": [99, 113, 122]},
    "San Antonio Spurs": {"Color 1": [196, 206, 211], "Color 2": [6, 25, 34]},
    "Toronto Raptors": {"Color 1": [206, 17, 65], "Color 2": [6, 25, 34]},
    "Utah Jazz": {"Color 1": [0, 43, 92], "Color 2": [0, 71, 27]},
    "Washington Wizards": {"Color 1": [0, 43, 92], "Color 2": [227, 24, 55]}
}

def setup_webdriver():
    try:
        options = Options()
        options.add_argument('--headless')
        driver_path = r"C:\Users\ahmad\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
        return webdriver.Chrome(executable_path=driver_path, options=options)
    except WebDriverException as e:
        print(f"Error setting up Chromedriver: {e}")
        exit(1)


def is_black_or_grey(rgb):
    return all([abs(int(c) - int(rgb[0])) < 50 for c in rgb])


def is_similar_color(color1, color2, threshold=10):
    return all([abs(c1 - c2) <= threshold for c1, c2 in zip(color1, color2)])

def get_top_colors(img):
    colors, count = np.unique(img.reshape(-1,3), axis=0, return_counts=True)
    sorted_colors = colors[count.argsort()[::-1]]
    top_colors = []
    for color in sorted_colors:
        if not top_colors or not is_similar_color(color, top_colors[0], threshold=10):
            top_colors.append([int(channel) for channel in color])
        if len(top_colors) == 2:
            break
    return {"first_color": top_colors[0], "second_color": top_colors[1] if len(top_colors) > 1 else None}


def get_team_colors(driver, team_name):
    print(f"Processing jerseys for {team_name}...")
    url = f"https://lockervision.nba.com/team/{team_name}"
    driver.get(url)
    img_urls = [img.get_attribute('src') for img in driver.find_elements_by_css_selector('.MuiCardMedia-root img')]
    team_colors = {}
    formatted_team_name = team_name.replace('-', ' ').title()  # Convert to the format used in nba_teams
    for img_url in img_urls:
        jersey_type = img_url.split('/')[-1].split('.')[0]

        # Remove the first three letters
        jersey_type = jersey_type[4:]

        # Replace abbreviations with full names
        jersey_type = jersey_type.replace("AE", "Association Edition")
        jersey_type = jersey_type.replace("IE", "Icon Edition")
        jersey_type = jersey_type.replace("CE", "City Edition")
        jersey_type = jersey_type.replace("SE", "Statement Edition")
        jersey_type = jersey_type.replace("CLE", "Classic Edition")
        jersey_type = jersey_type.replace("ME", "Mamba Edition")

        print(f"Processing {jersey_type}...")
       
        if "Association Edition" in jersey_type:
            # For Association Edition, first color is white and second color is Color 1
            team_colors[jersey_type] = {"first_color": nba_teams[formatted_team_name]["Color 1"], 
                                        "second_color": [255, 255, 255]}
        elif "Icon Edition" in jersey_type:
            # For Icon Edition, first color is Color 1 and second color is Color 2
            team_colors[jersey_type] = {"first_color": nba_teams[formatted_team_name]["Color 1"], 
                                        "second_color": nba_teams[formatted_team_name]["Color 2"]}
        else:
            # Extract colors from the website for other editions
            img_data = requests.get(img_url).content
            with open('temp.jpg', 'wb') as handler:
                handler.write(img_data)
            img = Image.open('temp.jpg')
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.2)  # Increase saturation by 20%
            width, height = img.size
            left = (width - 109)/2
            top = (height - 109)/2
            right = (width + 109)/2
            bottom = (height + 109)/2
            img = img.crop((left, top, right, bottom))
            img = np.array(img)
            team_colors[jersey_type] = get_top_colors(img)
   
    return team_colors


def main():
    teams = ["atlanta-hawks", "boston-celtics", "brooklyn-nets", "charlotte-hornets",
             "chicago-bulls", "cleveland-cavaliers", "dallas-mavericks", "denver-nuggets",
             "detroit-pistons", "golden-state-warriors", "houston-rockets", "indiana-pacers",
             "la-clippers", "los-angeles-lakers", "memphis-grizzlies", "miami-heat",
             "milwaukee-bucks", "minnesota-timberwolves", "new-orleans-pelicans", "new-york-knicks",
             "oklahoma-city-thunder", "orlando-magic", "philadelphia-76ers", "phoenix-suns",
             "portland-trail-blazers", "sacramento-kings", "san-antonio-spurs", "toronto-raptors",
             "utah-jazz", "washington-wizards"]

    nba_colors = {}
    driver = setup_webdriver()
    for team in teams:
        time.sleep(1)
        team_title_case = team.replace('-', ' ').title()  # Convert to title case for JSON
        nba_colors[team_title_case] = get_team_colors(driver, team)
        print(f"Done with {team}.")

    with open(r"C:\Users\ahmad\NBA-Gameday-Generator\nba_colors.json", 'w') as f:
        json.dump(nba_colors, f, indent=4)

    driver.quit()

if __name__ == "__main__":
    main()




