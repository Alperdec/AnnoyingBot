import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

def normalize_name(user_id):
    index = 0
    for letter in user_id:
        if letter == '#':
            return user_id[:index]
        else:
            index +=1


class pointSystem:
    def __init__(self):
        self.url = os.getenv('DB_API_URL')
        self.data = []

    def increment_user(self, user_id, points):
        payload = {'points': int(points)}
        req = requests.put(self.url + '/users/' + user_id, data=payload)
        if req.status_code == 404: 
            return self.create_new_user(user_id, points=points)
        else: 
            return req.status_code

    def create_new_user(self, user_id, points = 1):
        payload = {'name': user_id, 'points': int(points)}
        req = requests.post(self.url, data=payload)

        return req.status_code

    def get_user(self, user_id):
        req = requests.get(self.url + '/users/' + user_id)
        if req.status_code == 404: 
            return("user does not exist")
        else: 
            return req.json()["points"]

    def sort_descending(self):
        self.data = sorted(self.data, key = lambda i : i['points'], reverse=True)
        return self.data

    def get_all_users(self):
        req = requests.get(self.url)
        self.data = req.json()

        return self.sort_descending()