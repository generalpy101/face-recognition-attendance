import json
import requests
import base64
import os
import time
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("BASE_URL")


class FaceDetection:
    def __init__(self, base_url) -> None:
        self.base_url = base_url
        self.base_headers = headers = {
            "Ocp-Apim-Subscription-Key": os.getenv("Ocp-Apim-Subscription-Key"),
            "Ocp-Apim-Subscription-Region": os.getenv("Ocp-Apim-Subscription-Region"),
        }
        
    def DeletePerson(self,personGroupId,personId) :
        url = self.base_url + "/persongroups/" + personGroupId + "/persons/" + personId
        r = requests.delete(url,headers=self.base_headers)
        if r.status_code == 200 :
            self._trainModel(personGroupId=personGroupId)
            return True
        return False

    def DetectPerson(self, personGroupId, image):
        url = self.base_url + "/detect"
        headers = {
            **self.base_headers,
            "Content-Type": "application/octet-stream",
        }
        params = {
            "recognitionModel": "recognition_03",
            "detectionModel": "detection_03",
        }

        r = requests.post(
            url, params=params, data=image, headers=headers
        )
        print(json.dumps(r.json()))
        if r.status_code == 200:
            j = r.json()
            return j

    def _checkModelTraininStatus(self,personGroupId) :
        url = self.base_url + "/persongroups/" + personGroupId + "/training"
        headers = {
            **self.base_headers,
            "Content-Type": "application/json",
        }
        r = requests.get(url,headers=headers)
        res = r.json()
        if res["status"] == "succeeded" :
            return True
        return False 
    
    def IdentifyFace(self, personGroupId, image, max_threshold, maxCandidates):
        url = self.base_url + "/identify"
        headers = {
            **self.base_headers,
            "Content-Type": "application/json",
        }
        persons = self.DetectPerson(personGroupId, image)
        reqJson = {
            "personGroupId": personGroupId,
            "maxNumOfCandidatesReturned": maxCandidates,
            "confidenceThreshold": max_threshold,
            "faceIds": [],
        }
        if len(persons) > 0 :
            for i in persons :
                reqJson["faceIds"].append(i["faceId"])
        r = requests.post(url, json=reqJson, headers=headers)
        print(r.json())
        if type(r.json()) != type([]) and r.json().get("error",None) != None :
            print("Not trained training")
            self._trainModel(personGroupId=personGroupId)
            return None
        if r.status_code == 200:
            dat = r.json()
            results = []
            try:
                if len(dat) > 0 :
                    for i in dat :
                        if not (len(i.get("candidates")) > 0) : continue
                        pId = i.get("candidates")[0].get("personId")
                        personData = self._getPerson(personGroupId, pId)
                        name = personData.get('name')
                        uuid = personData.get("personId")
                        results.append(uuid)
                        print(f"Hello {name}")
                return results
            except Exception as e:
                print(e)
                return None

    def _trainModel(self, personGroupId):
        url = self.base_url + "/persongroups/" + personGroupId + "/train"
        headers = {
            **self.base_headers,
            "Content-Type": "application/json",
        }
        r = requests.post(url, headers=headers)
        if r.status_code == 202 :
            print("model training queued")

    def _getPerson(self, personGroupId, personId):
        url = (
            self.base_url
            + "/persongroups/"
            + personGroupId
            + "/persons/"
            + str(personId)
        )
        headers = {
            **self.base_headers,
            "Content-Type": "application/json",
        }
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            dat = r.json()
            print(json.dumps(dat))
            return dat

    def AddPersonToPersonGroup(self, personGroupId, name, regNo, images):
        imageBase64s = []
        print(name, regNo)

        body = {"name": name, "userData": regNo}
        headers = {
            **self.base_headers,
            "Content-Type": "application/json",
        }
        url = self.base_url + "/persongroups/" + str(personGroupId) + "/persons"
        res = requests.post(url, json=body, headers=headers)
        if res.status_code == 200:
            personId = res.json()["personId"]
            print(json.dumps(res.json()))
            url = (
                self.base_url
                + "/persongroups/"
                + str(personGroupId)
                + "/persons/"
                + personId
                + "/persistedFaces"
            )
            params = {"detectionModel": "detection_03"}
            headers = {
                **self.base_headers,
                "Content-Type": "application/octet-stream",
            }
            for i in images:
                # data = open(i, "rb").read()
                r = requests.post(url, headers=headers, params=params, data=i)
                print(json.dumps(r.json()))
                if r.status_code == 200:
                    print("Success")
            self._trainModel(personGroupId)
            return personId

    def CreatePersonGroup(self, personGroupName):
        url = self.base_url + "/persongroups/" + personGroupName
        jsonDat = {
            "name": personGroupName,
            "userData": "user-provided data attached to the person group.",
            "recognitionModel": "recognition_03",
        }
        headers = {
            **self.base_headers,
            "Content-Type": "application/json",
        }
        r = requests.put(url, headers=headers, json=jsonDat)
        if r.status_code == 200:
            print("User group created successfully")


if __name__== "__main__" :
    f = FaceDetection(URL)
    f._trainModel("test1")
