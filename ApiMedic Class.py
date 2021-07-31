import requests
import hmac
import base64
import json

class DiagnosisClient:

    def __init__(self, username, password, authServiceUrl, language, healthServiceUrl):
        self._language = language
        self._healthServiceUrl = healthServiceUrl
        self._token = self._loadToken(username, password, authServiceUrl)


    def _loadToken(self, username, password, url):
        rawHashString = hmac.new(bytes(password, encoding='utf-8'), url.encode('utf-8')).digest()
        computedHashString = base64.b64encode(rawHashString).decode()
        bearer_credentials = username + ':' + computedHashString
        postHeaders = {
               'Authorization': f'Bearer {bearer_credentials}'
        }
        responsePost = requests.post(url, headers=postHeaders)
        data = json.loads(responsePost.text)
        return data
    
    def _loadFromWebService(self, action):
        extraArgs = "token=" + self._token["Token"] + "&format=json&language=" + self._language
        if "?" not in action:
            action += "?" + extraArgs
        else:
            action += "&" + extraArgs
        url = self._healthServiceUrl + "/" + action
        response = requests.get(url)
        data = json.loads(response.text)
        return data       

    
    def loadIssues(self):
        return self._loadFromWebService("issues")

    def loadIssueInfo(self, issueId):
        issueId = str(issueId)
        action = f"issues/{issueId}/info"
        return self._loadFromWebService(action)

    def loadSymptoms(self):
        return self._loadFromWebService("symptoms")


    def loadDiagnosis(self, selectedSymptoms, gender, yearOfBirth):
        serializedSymptoms = json.dumps(selectedSymptoms)
        action = f"diagnosis?symptoms={serializedSymptoms}&gender={gender}&year_of_birth={yearOfBirth}"
        return self._loadFromWebService(action)    
    