import requests
import datetime


class EcoleDirect:
    """ Permet de se connecter et faire des requetes a l'API d'école direct
    Allow to connect and make requests to Ecoledirect's API """

    def __init__(self, username=None, password=None):
        """Create a new EcoleDirect object"""

        self.token = None
        self.id = None
        if username is not None and password is not None:
            self.connect(username, password)

    def __req(self, url, payload):
        """this function make all requests to the api"""
        return requests.post(url, data=payload)

    def connect(self, username: str, password: str):
        """create an connection to the API"""

        path = 'https://api.ecoledirecte.com/v3/login.awp'
        args = """data={}"identifiant": "{}","motdepasse": "{}"{}"""
        args = args.format("{", username, password, "}")
        connection = self.__req(path, args)
        if connection.json()['code'] != 200:
            print("error ! bad username or password")
        else:
            self.token = connection.json()['token']
            self.id = connection.json()['data']['accounts'][0]['id']

    def getWT(self, startDate=datetime.date.today().strftime("%Y-%m-%d"),
              endDate=(datetime.date.today() + datetime.timedelta(days=6)).strftime("%Y-%m-%d")):
        """get the work time from the api"""
        if self.token is None or self.id is None:
            print("Error connection must be acitvate")
            return

        path = 'https://api.ecoledirecte.com/v3/E/{}/emploidutemps.awp?verbe=get&'.format(self.id)
        args = 'data={}"token":"{}","dateDebut": "{}","dateFin": "{}","avecTrous": false,{}'
        args = args.format("{", self.token, startDate, endDate, "}")
        connection = self.__req(path, args)
        if connection.json()['code'] != 200:
            print("error ! bad username or password")
        else:
            # self.token = connection.json()['token']
            return connection.json()['data']

    def getHW(self):
        """get homework from the api"""
        if self.token is None or self.id is None:
            print("Error connection must be acitvate")
            return

        path = f'https://api.ecoledirecte.com/v3/Eleves/{self.id}/cahierdetexte.awp?verbe=get&'
        args = """data={}"token":"{}"{}""".format("{", self.token, "}")
        connection = self.__req(path, args)
        if connection.json()['code'] != 200:
            print("error ! bad username or password")
        else:
            # self.token = connection.json()['token']
            return connection.json()['data']

    def getNotes(self):
        """get notes from the api"""
        if self.token is None or self.id is None:
            print("Error connection must be acitvate")
            return

        path = f'https://api.ecoledirecte.com/v3/eleves/{self.id}/notes.awp?verbe=get&'
        args = """data={}"token":"{}"{}""".format("{", self.token, "}")
        connection = self.__req(path, args)
        if connection.json()['code'] != 200:
            print("error ! bad username or password")
        else:
            # self.token = connection.json()['token']
            return connection.json()['data']

    def getSL(self):
        """get sochlar life from the API"""
        if self.token is None or self.id is None:
            print("Error connection must be acitvate")
            return

        path = f'https://api.ecoledirecte.com/v3/eleves/{self.id}/viescolaire.awp?verbe=get&='
        args = """data={}"token":"{}"{}""".format("{", self.token, "}")
        connection = self.__req(path, args)
        if connection.json()['code'] != 200:
            print("error ! bad username or password")
        else:
            # self.token = connection.json()['token']
            return connection.json()['data']

    def getCloud(self):
        """get the cloud from the API"""
        if self.token is None or self.id is None:
            print("Error connection must be acitvate")
            return

        path = f'https://api.ecoledirecte.com/v3/cloud/E/{self.id}.awp?verbe=get&='
        args = """data={}"token":"{}"{}""".format("{", self.token, "}")
        connection = self.__req(path, args)
        if connection.json()['code'] != 200:
            print("error ! bad username or password")
        else:
            # self.token = connection.json()['token']
            return connection.json()['data']
