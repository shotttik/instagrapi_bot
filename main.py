import sys
import time
import traceback
from Models.models import UserShort
from hashtag import search_media_by_hashtag
from location import search_media_by_location
import json
from instagrapi import Client
import config
import json
from Models.models import *
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def write_to_json_file(data):
    # Specify the file path
    file_path = "output.json"
    # # Write the dictionary to a JSON file
    with open(file_path, 'w') as json_file:
        json_file.write(json.dumps(data))
        json_file.close()


def analyze(cl, cur_user: UserShort):
    # Lists to store user data
    try:
        # Checking if the user is not in the users list, not in the blacklist, and not already analyzed
        if cur_user.pk not in users and cur_user.pk not in blacklist:
            # Retrieving user information from Instagram API
            user_dict_from_api = cl.user_info_by_username(
                cur_user.username).dict()
            cur_user_info = UserInfo(user_dict_from_api)

            try:

                # Checking follower count range
                if cur_user_info.follower_count > min_followers and cur_user_info.follower_count < max_followers:
                    time.sleep(0.5)
                    scope = [
                        "https://spreadsheets.google.com/feeds",
                        "https://www.googleapis.com/auth/drive"]
                    creds = ServiceAccountCredentials.from_json_keyfile_name(
                        'client_secret.json', scope)
                    client = gspread.authorize(creds)
                    sheet = client.open(google_doc).sheet1
                    row = cur_user_info.row_string.split(";")
                    sheet.insert_row(row, 2)
                    users.append(cur_user.pk)

                    # Appending the result to the CSV file
                    with open("result.csv", "a", encoding='utf-8') as r:
                        r.write(cur_user_info.row_string)

                    # Displaying the total count of business accounts saved
                    total_counter = len(sheet.get_all_values()) - 1
                    print(
                        f"Account saved, {total_counter} in total")
                else:
                    # Adding the user to the blacklist if follower count is out of range
                    blacklist.append(cur_user.pk)
                    try:
                        with open('log.txt', 'a', encoding='utf-8') as b:
                            b.write(f'{cur_user.pk}\n')
                    except:
                        pass

                    # Appending user data to the 'rubbish.csv' file
                    with open("rubbish.csv", "a", encoding='utf-8') as r:
                        r.write(cur_user_info.row_string)
            except:
                # Handling exceptions and printing traceback
                print(traceback.format_exc())

            # Adding a sleep delay after processing each user
            time.sleep(2.75)
    except:
        # Handling exceptions and printing traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    # Lists to store user data and blacklist
    users = []  # List to store user IDs
    blacklist = []  # List to store blacklisted user IDs

    # Retrieving Instagram credentials and settings from the 'config' module
    username = config.LOGIN
    password = config.PASSWORD

    if config.TYPE == "location" and type(config.TARGET) is not tuple:
        print("config TARGET must be datatype of tuple (46.22, 2.21)")
        sys.exit()
    # Handling optional configuration settings with default values
    try:
        max_followers = int(config.MAX_FOLLOWERS)
    except:
        max_followers = 25000

    try:
        min_followers = int(config.MIN_FOLLOWERS)
    except:
        min_followers = 250

    try:
        google_doc = str(config.GOOGLE_DOC)
    except:
        google_doc = 'TEST'

    # Creating or updating the 'log.txt' file
    with open('log.txt', 'a', encoding='utf-8') as b:
        pass

    # Reading the 'log.txt' file to populate the blacklist
    with open("log.txt", "r", encoding="utf-8") as f:
        for line in f:
            blacklist.append(int(line.strip()))

    try:
        header_string = UserInfo.get_row_header_string()
        # Creating or updating the 'result.csv' file
        with open("result.csv", "x", encoding="utf-8") as t:
            t.write(
                header_string + "\n")
            row = header_string.split(";")

            # Authenticating with Google Sheets API
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                'client_secret.json', scope)
            client = gspread.authorize(creds)
            sheet = client.open(google_doc).sheet1

            # Inserting the header row into the Google Sheet
            sheet.insert_row(row, 1)
    except:
        pass

    # Populating the 'users' list with user IDs from 'result.csv'
    with open("result.csv", "r", encoding="utf-8") as f:
        for line in f:
            users.append(line.strip().split(';')[0])
        try:
            users.remove('id')
        except:
            pass

    print("Blacklist refreshed")
    cl = Client()
    cl.login(username, password)
    parsed_data = []
    target = config.TARGET
    if config.TYPE == "location":
        parsed_data, target = search_media_by_location(cl)
    elif config.TYPE == "hashtag":
        parsed_data = search_media_by_hashtag(cl)
    else:
        "Wrong type of search.. please use 'location' or 'hashtag'"
    for user_data in parsed_data:
        analyze(cl, user_data)
    print("Finished")
    cl.logout()
