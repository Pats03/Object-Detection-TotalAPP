class User:
    def __init__(self, email, password,name):
        self.email = email
        self.password = password
        self.name=name

    def save_to_db(self, mongo):
        try:
            mongo.db.users.insert_one({"email": self.email, "name":self.name,"password": self.password})
        except Exception as e:
            raise e

    @staticmethod
    def find_by_username(mongo, email):
        return mongo.db.users.find_one({"email": email})
