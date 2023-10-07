import re
import pandas as pd

def preprocess(data):
    def convert24(str1):

        # Checking if last two elements of time
        # is AM and first two elements are 12
        if str1[-2:] == "AM" and str1[:2] == "12":
            return "00" + str1[2:-2]

        # remove the AM
        elif str1[-2:] == "AM":
            return str1[:-2]

        # Checking if last two elements of time
        # is PM and first two elements are 12
        elif str1[-2:] == "PM" and str1[:2] == "12":
            return str1[:-2]

        else:

            # add 12 to hours and remove PM
            return str(int(str1[:1]) + 12) + str1[1:8] if ':' in str1[:2] else str(int(str1[:2]) + 12) + str1[2:8]

    data2 = ""
    substring = ""
    data2 = data.replace("[", " ")
    data2 = data2.replace("]", " ")
    data2 = data2.replace("~", "-")
    data = data2

    pattern = r'\s\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{1,2}:\d{1,2}\s\S[AMP]\s\s-'

    #Extracting messages from the dataset
    messages = re.split(pattern, data)
    msg = []
    for i in messages:
        i = i.replace('\u202f', '')
        i = i.replace('\n', '')
        i = i.replace('\u200e', '')
        i = i.replace('atasnim w3spaces', '')
        msg.append(i)

    messages = msg
    messages = messages[:-1]

    #Extracting dates from the dataset
    dates = re.findall(pattern, data)
    D = []
    for i in dates:
        i = i.strip()
        r = '\d{1,2}:\d{1,2}:\d{1,2}\s\S[AMP]'
        sbstr = re.search(r, i)
        i = i.replace(sbstr[0], convert24(sbstr[0]))
        D.append(i)
    dates = D

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    # convert message_date type
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M:%S -')
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # separate users and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df = df[df['message'] != '']
    return df