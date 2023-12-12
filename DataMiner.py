#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Importing necessary libraries and modules
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from random import randint, choice
from emoji import demojize
from datetime import datetime
from time import sleep, time
import traceback
from InstagramAPI import InstagramAPI
import config  # Assuming 'config' contains required configuration settings

# Function to perform Instagram user analysis based on location


def loc_based(api, target):
    # Searching for locations on Instagram
    api.searchLocation(target)

    # Iterating through the locations found
    for loca in api.LastJson['items']:
        location = str(loca['location'].get('pk', ''))
        next_max_id = True
        counter = 0

        # Iterating through location feed
        while next_max_id:
            if next_max_id is True:
                next_max_id = ''
            _ = api.getLocationFeed(location, maxid=next_max_id)
            js = api.LastJson
            sleep(1)

            # Analyzing each user in the location feed
            for i in js['items']:
                cur_user = i['user']['pk']
                analyze(api, cur_user, target)
                counter += 1

                # Limiting the number of users to be analyzed
                if counter > parse_limit:
                    return
            sleep(1)
            api.LastJson = js
            try:
                next_max_id = api.LastJson.get('next_max_id', '')
            except:
                return

# Function to perform Instagram user analysis based on hashtags


def hash_based(api, hashtags):
    next_max_id = True

    # Iterating through each provided hashtag
    for hashtag in hashtags:
        local_counter = 0
        next_max_id = True

        # Iterating through hashtag feed
        while next_max_id and local_counter <= parse_limit:
            if next_max_id is True:
                next_max_id = ''
            try:
                _ = api.getHashtagFeed(hashtag, maxid=next_max_id)
            except:
                sleep(1)
                _ = api.getHashtagFeed(hashtag, maxid=next_max_id)
            js = api.LastJson
            sleep(1)

            # Analyzing each user in the hashtag feed
            for i in js['items']:
                cur_user = i['user']['pk']
                analyze(api, cur_user, hashtag)
                local_counter += 1
                print(f"{local_counter} was analyzed")

                # Limiting the number of users to be analyzed
                if local_counter >= parse_limit:
                    break
            sleep(1)
            api.LastJson = js
            try:
                next_max_id = api.LastJson.get('next_max_id', '')
            except:
                return


# Function to perform Instagram user analysis based on a specific user
def user_based(api, target):
    # Searching for a specific Instagram user
    api.searchUsername(target)
    target_id = str(api.LastJson.get('user', "").get("pk", ""))
    sleep(0.5)

    # Retrieving total followers of the specified user
    getTotalFollowers(api, target_id)


# Function to retrieve total followers of a user
def getTotalFollowers(api, user_id):
    usrs = []
    next_max_id = True

    # Iterating through the user's followers
    while next_max_id:
        if next_max_id is True:
            next_max_id = ''
        _ = api.getUserFollowers(user_id, maxid=next_max_id)
        j = api.LastJson

        # Analyzing each follower
        for i in j['users']:
            cur_user = i['pk']
            usrs.append(cur_user)
            analyze(api, cur_user, target)

            # Limiting the number of followers to be analyzed
            if len(usrs) > parse_limit:
                print(f"Parsed: {str(len(usrs))}")
                sleep(2.5)
                print("All users parsed")
                return
        api.LastJson = j
        next_max_id = api.LastJson.get('next_max_id', '')
        print(f"Parsed: {str(len(usrs))}")
        sleep(randint(2, 3))
    print("All users parsed")

# Function to analyze an Instagram user and save relevant information


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

            # Handling rate limit (429 status code)
            while api.LastResponse.status_code == "429":
                sleep(3)
                api.getUsernameInfo(cur_user)
            jz = api.LastJson

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
                        sleep(0.5)
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
                            users.append(cur_user)

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
            sleep(2.75)
    except:
        # Handling exceptions and printing traceback
        print(traceback.format_exc())


if __name__ == '__main__':
    # Lists to store user data and blacklist
    users = []  # List to store user IDs
    blacklist = []  # List to store blacklisted user IDs

    print("Start")

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

    # Initializing the Instagram API
    api = InstagramAPI(username, password)
    api.login()
    print("CANT LOGIN")
    # Choosing the appropriate function based on the provided 'type'
    if str(type) in ['hashtag', 'hash', 'hashtags']:
        target = str(config.TARGET).split(',')
        hash_based(api, target)
    elif str(type) in ['loc', 'location', 'locations']:
        target = str(config.TARGET)
        loc_based(api, target)
    else:
        target = str(config.TARGET)
        user_based(api, target)

    print("Finished")

    # Logging out of the Instagram API
    api.logout()
