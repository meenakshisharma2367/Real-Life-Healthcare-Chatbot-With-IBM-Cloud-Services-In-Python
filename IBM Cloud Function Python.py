#
#
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#
import sys

def main(args):
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
        
    d = DiagnosisClient(username="s2NEp_GMAIL_COM_AUT",language="en-gb",healthServiceUrl="https://healthservice.priaid.ch",authServiceUrl="https://authservice.priaid.ch/login",password="f9H6Brm5Z3NyFk8p7")
        
    option = args.get("option")
    issue = args.get("issue")
    symptom_1 = args.get("symptom_1")
    symptom_2 = args.get("symptom_2")
    symptom_3 = args.get("symptom_3")
    if int(option) == 1:
        issues_1 = d.loadIssues()
        for ism in issues_1:
            if issue.lower() == ism["Name"].lower():
                issues = d.loadIssueInfo(int(ism["ID"]))
    if int(option) == 2:
        symptoms = d.loadSymptoms()
        sym_id = []
        gender = args.get("gender","")
        yob = args.get("yob","")
        if symptom_1:
            for i in symptoms:
                if i["Name"].lower() == symptom_1.lower():
                    sym_id.append(i["ID"])
        if symptom_2:
            for i in symptoms:
                if i["Name"].lower() == symptom_2.lower():
                    sym_id.append(i["ID"])
        if symptom_3:
            for i in symptoms:
                if i["Name"].lower() == symptom_3.lower():
                    sym_id.append(i["ID"])
                  
        do = d.loadDiagnosis(gender=gender,yearOfBirth=int(yob),selectedSymptoms=sym_id)
        if do:
            issues = {"Message":""}
            for i in range(len(do)):
                if len(do)-1 == i:
                    issues["Message"] = issues["Message"]+ do[i]["Issue"]["Name"] + " (Accuracy: " + str(do[i]["Issue"]["Accuracy"])[:4] +"% ) "
                elif len(do)-2==  i:
                    issues["Message"] = issues["Message"]+ do[i]["Issue"]["Name"] + " (Accuracy: " + str(do[i]["Issue"]["Accuracy"])[:4] +"% ) "+" and "
                else:
                    issues["Message"] = issues["Message"]+ do[i]["Issue"]["Name"] + " (Accuracy: " + str(do[i]["Issue"]["Accuracy"])[:4] +"% ) "+" , "
        else:
            issues = {"Message":"I could not diagnose by entered symptoms."} 
            
    return issues
