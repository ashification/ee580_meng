import json


class GFG_User(object):
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name


user = GFG_User(first_name="Jake", last_name="Doyle")
json_data = json.dumps(user.__dict__)
print(json_data)
print(GFG_User(**json.loads(json_data)))
test = GFG_User(**json.loads(json_data))
print(test.first_name)