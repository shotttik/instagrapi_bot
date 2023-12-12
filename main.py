from random import choice
import re
import sys
import time
import traceback

from emoji import demojize
from hashtag import search_media_by_hashtag
from location import search_media_by_location
from main import cl
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


def analyze(api, cur_user, target):
    # Lists to store user data
    com_counter = []  # List to store comment counts
    locations = []  # List to store locations
    tags = []  # List to store hashtags
    pattern = "#(\w+)"  # Regular expression pattern for extracting hashtags

    try:
        # Checking if the user is not in the users list, not in the blacklist, and not already analyzed
        if str(cur_user) not in users and int(cur_user) not in blacklist and str(cur_user) not in blacklist and int(cur_user) not in users:
            # Retrieving user information from Instagram API
            api.getUsernameInfo(cur_user)

            try:
                # Checking if the user is a business account
                business = jz['user']['is_business']
            except:
                business = False

            try:
                if business:
                    user = jz['user']['username']
                    email = jz['user']['public_email']
                    category = jz['user']['category']
                    name = jz['user']['full_name']
                    follower_count = int(jz['user']['follower_count'])
                    following_count = jz['user']['following_count']

                    # Handling optional user location information
                    try:
                        location = jz['user']['city_name']
                    except:
                        location = ""

                    contact_phone_number = jz['user']['contact_phone_number']
                    site = jz['user']['external_url']
                    posts_number = int(jz['user']['media_count'])

                    # Checking follower count range
                    if follower_count > min_followers and follower_count < max_followers:
                        time.sleep(0.5)
                        api.getUserFeed(cur_user)
                        jt = api.LastJson

                        # Analyzing each post in the user's feed
                        for post in jt['items']:
                            try:
                                com_counter.append(str(post['comment_count']))
                            except:
                                com_counter.append("0")
                            try:
                                caption = str(
                                    demojize(post['caption']['text']))
                                tags.extend(re.findall(pattern, caption))
                            except:
                                pass
                            try:
                                locations.append(post['location']['name'])
                            except:
                                pass
                        tags = list(set(tags))

                        # Handling empty location
                        if str(location) == "":
                            try:
                                location = choice(locations)
                            except:
                                location = ""

                        # Checking for email and saving information to Google Sheets and CSV
                        if email:
                            scope = ['https://spreadsheets.google.com/feeds',
                                     'https://www.googleapis.com/auth/drive']
                            creds = ServiceAccountCredentials.from_json_keyfile_name(
                                'client_secret.json', scope)
                            client = gspread.authorize(creds)
                            sheet = client.open(google_doc).sheet1
                            row = f"{cur_user};{user};{email};{name};{category};{contact_phone_number};{site};{follower_count};{following_count};{posts_number};{target};{location};{com_counter[0]};{com_counter[1]};{com_counter[2]};{com_counter[3]};{com_counter[4]};{com_counter[5]};{com_counter[6]};{com_counter[7]};{com_counter[8]};{com_counter[9]}\n".split(
                                ";")
                            sheet.insert_row(row, 2)
                            users.append(cur_user["pk"])

                            # Appending the result to the CSV file
                            with open("result.csv", "a", encoding='utf-8') as r:
                                r.write(
                                    f"{cur_user};{user};{email};{name};{category};{contact_phone_number};{site};{follower_count};{following_count};{posts_number};{target};{location};{com_counter[0]};{com_counter[1]};{com_counter[2]};{com_counter[3]};{com_counter[4]};{com_counter[5]};{com_counter[6]};{com_counter[7]};{com_counter[8]};{com_counter[9]}\n")

                            # Displaying the total count of business accounts saved
                            total_counter = len(sheet.get_all_values()) - 1
                            print(
                                f"Business account saved, {total_counter} in total")
                        else:
                            # Adding the user to the blacklist if email is not available
                            blacklist.append(cur_user)
                            try:
                                with open('log.txt', 'a', encoding='utf-8') as b:
                                    b.write(f'{cur_user}\n')
                            except:
                                pass
                    else:
                        # Adding the user to the blacklist if follower count is out of range
                        blacklist.append(cur_user)
                        try:
                            with open('log.txt', 'a', encoding='utf-8') as b:
                                b.write(f'{cur_user}\n')
                        except:
                            pass

                        # Appending user data to the 'rubbish.csv' file
                        with open("rubbish.csv", "a", encoding='utf-8') as r:
                            r.write(
                                f"{cur_user};{user};{email};{name};{category};{contact_phone_number};{site};{follower_count};{following_count};{posts_number};{target};{location}\n")
                else:
                    # Adding the user to the blacklist if not a business account
                    blacklist.append(cur_user)
                    try:
                        with open('log.txt', 'a', encoding='utf-8') as b:
                            b.write(f'{cur_user}\n')
                    except:
                        pass
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
    type = config.TYPE

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
        parse_limit = int(config.LIMIT)
    except:
        parse_limit = 1000

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
        # Creating or updating the 'result.csv' file
        with open("result.csv", "x", encoding="utf-8") as t:
            t.write(
                "id;username;email;name;category;phone;URL;followers;followings;posts_number;searching;location\n")
            row = "id;username;email;name;category;phone;URL;followers;followings;posts_number;searching;location".split(
                ";")

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
        analyze(cl, user_data, target)
    print("Finished")
    cl.logout()
