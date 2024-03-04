#!/usr/bin/env python3
import requests as req
import time
import os
import json
import random

url = "http://0.0.0.0:8080"

def defaultBehaviour():
    f = open("../artists-list.csv", "r")
    lines = f.readlines()

    for line in lines:
        components = line.split(",")
        schema = json.loads("{}")

        descriptor = os.open(path=f"../data/{components[0]}.json",flags=(os.O_WRONLY | os.O_CREAT | os.O_TRUNC),mode=0o777)
        f1 = open(descriptor, "w")

        ids = components[1:]
        if len(ids) > 1:
            ids = ids[:-1]

        for i in ids:
            i = i.replace("\n", "")
            resp = req.get(f"{url}/artistInsights?artistid={i}")
            if resp.status_code != 200:
                print("Error:", components[0], resp.status_code)
                f2 = open("errors.txt", "a")
                f2.write(f"{components[0]} {resp.status_code} {i}\n")
                f2.close()
            else:
                print("Writing:", components[0])
                rsp = json.loads(resp.text)

                if not schema:
                    schema = rsp
                    trash = schema["data"]["globalChartPosition"]
                else:
                    percentage = int(components[-1]) / 100

                    schema["data"]["globalChartPosition"] += rsp["data"]["globalChartPosition"]
                    if "monthlyListeners" in schema["data"] and "monthlyListeners" in rsp["data"]:
                        schema["data"]["monthlyListeners"] += int(rsp["data"]["monthlyListeners"] * percentage)

                    if "monthlyListenersDelta" in schema["data"] and "monthlyListenersDelta" in rsp["data"]:
                        schema["data"]["monthlyListenersDelta"] += int(rsp["data"]["monthlyListenersDelta"] * percentage)

                    schema["data"]["followerCount"] += int(rsp["data"]["followerCount"] * percentage)
                    schema["data"]["followingCount"] += int(rsp["data"]["followingCount"] * percentage)
                    # TODO: Merge cities data


        if schema:
            f1.write(json.dumps(schema))
        f1.close()

        sleepTime = random.randint(100, 300)
        time.sleep(sleepTime / 100)

def main():
    os.umask(0)
    defaultBehaviour()

main()
