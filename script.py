# installing
!pip install phonenumbers
!pip install numpy
!pip install langdetect

# imports and magics
import os
import re
import string
import nltk
import pandas as pd
import numpy as np
from collections import defaultdict
from itertools import chain
import phonenumbers
from langdetect import detect

print('Enter your filename: ')
FILENAME = input()

print('Enter filetype: excel or csv : ')
 file_type = input()
 if file_type == 'excel':
    dataset = pd.ExcelFile(FILENAME)

    print("Sheet names are in the file are : ", dataset.sheet_names)
    print("Please enter the sheet name of the file you want to read :")
    SHEET_NAME = input()
    df_cases = dataset.parse(SHEET_NAME)


elif file_type == 'csv':
    print('Enter the delimiter: for example -> ; or , or :')
    DELIMITER = input()
    df_cases = pd.read_csv(FILENAME, encoding = 'utf8', sep=DELIMITER)



print('Enter the names of the columns that you would want to anonymize. These are all the column names : ')
print(list(df_cases))
anonymize_COLUMNS = input()

column_list  = anonymize_COLUMNS.split(",")
print('The columns that you have seleceted are: \n')
print(column_list)
print()

print("\nThis is how 1 row of the dataset looks:\n")

data=df_cases.reset_index(drop=True)
data.head(1)

lang_filter = input('\nEnter "y" if you would like to continue with Language Filtering. \nEnter "n" if you want to skip Language Filtering')

if lang_filter == 'y':

    #lang detection

    data['lang_detected']=""


    for i in range(0,len(data)):
        lang = detect(data[column_list[0]][i])
        data['lang_detected'][i]=lang

    print("\n----------------- LANG FILTER --------------------")
    print("\n The count of all the languages detected are: \n")
    print(data['lang_detected'].value_counts())

    # Drop all non-english languages
    data=data[data['lang_detected'] == 'en']

    print("\n--------------------------------------------------")
    print("\nAfter dropping Non-English language instances: \n")
    print(data['lang_detected'].value_counts())
    print("\n-------------- LANG FILTER COMPLETE---------------\n")

    data=data.reset_index(drop=True)


personal_filter = input('\nEnter "y" if you would like to continue with Personal Information Filtering. \nEnter "n" if you want to skip Personal Information Filtering')

if personal_filter == 'y':


    # email pattern, URLs,credit,twitter_pattern,system username

    email_url_pattern = re.compile(r"\b[a-zA-Z0-9_.+-:]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b|[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*|\b(?:\d[ -]*?){13,16}\b''|(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)|\b[IDCS][0-9]{6}\b)", re.IGNORECASE)


    #...........................................................................

    # code for removing phone num
    # use python phone numbers package to replace phone numbers
    # enter list of contry codes for which you expect phone numers, 'None' is default pattern

    region_list = ["DE", "US", "IN", "GB", "SG", "NL", None]

    def replace_phone(text, region):
        for reg in region:
            offset = 0
            cleaned = ""
            for match in phonenumbers.PhoneNumberMatcher(text, reg):
                cleaned += text[offset:match.start] + "{PHONENUMBER}"
                offset = match.end
            cleaned += text[offset:]
        return(cleaned)


    #...............................................................................

    ## remove personal names

    with open("female_names", 'r') as fin:
        female_names = [line.strip() for line in fin.readlines() if line.strip() != '']

    with open("male_names", 'r') as fin:
        male_names = [line.strip() for line in fin.readlines() if line.strip() != '']
    with open("surnames", 'r') as fin:
        surnames = [line.strip() for line in fin.readlines() if line.strip() != '']
    with open("german_names", 'r', encoding="utf-8", errors="ignore") as fin:
        german_names = [line.strip() for line in fin.readlines() if line.strip() != '']

    surnames.extend(german_names)

    # add additional names to these lists which you want to have removed

    custom_first_names =["Chin", "Onn", "Mah", "Wah", "Jee", "Turan"]
    custom_surnames =["Chow", "Matur","Ong"]

    # whitelist of words (in upper case) that should NOT be replaced even if they can be names
    whitelist =["AN", "IN", "AN", "OK," "JA", "PA", "PARIS", "MY", "CHINA", "HONG", "KONG"]

    # create regex patterns for names
    first_names = [name for name in chain(male_names, female_names, custom_first_names) if name not in whitelist]
    all_names=first_names+surnames+custom_surnames
    name_pattern_email= re.compile(r'\b(' + r'|'.join(all_names) + r')\b|\b[a-zA-Z0-9_.+-:]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b|[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*|\b(?:\d[ -]*?){13,16}\b''|(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)|\b[IDCS][0-9]{6}\b)', re.IGNORECASE)


 #..........running loop
for i in range(0,len(data)-1):
    for j in range(0,len(column_list)):
        data[column_list[j]][i] = re.sub(name_pattern_email, "{EMAIL/URL/Name}", data[column_list[j]][i])
        data[column_list[j]][i] = replace_phone(data[column_list[j]][i], region_list)

       # print(column_list[j])
print("\n----------------- PERSONAL INFORMATION FILTERING --------------------\n")
print("\n------- PRINTING 1 DATASET (after anonymization)---------\n ")

for i in range(0, len(column_list)):

    print(column_list[i], ": column in the first dataset looks like : \n")
    print(data[column_list[i]][0])
    print("--------------------------------------")
