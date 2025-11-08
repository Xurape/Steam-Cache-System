import json
import os
import time
import requests
from colorama import Fore
from dotenv import load_dotenv

"""

SteamCacheSystem
A system to cache and update Steam user data using the Steam API.

@author João Ferreira 
@version 1.0.0
@year 2023

"""
class SteamCacheSystem:
    def __init__(self):
        load_dotenv()
        self.API_KEY = os.getenv("STEAM_API_KEY")
        self.unknownAvatar = "https://i.imgur.com/c1UWC6V.png"
        self.debug = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "t")
        self.prefix = os.getenv("PREFIX", "[SteamCacheSystem]")

    """
    
    Caches the user data for a specific Steam ID by fetching information from the Steam API.
    @param id: The Steam ID of the user to cache.
    
    """
    def cacheUser(self, id):
        print(f"{self.prefix} {Fore.GREEN}Caching{Fore.RESET} SteamID: {Fore.CYAN}{id}{Fore.RESET}")
        file = f"{os.getcwd()}/data/{id}.json"
        currentTimestamp = int(time.time())

        if len(id) != 17:
            return print(f"{self.prefix} {Fore.RED}Invalid SteamID...")

        os.makedirs(os.path.dirname(file), exist_ok=True)

        if not os.path.exists(file):
            response = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={self.API_KEY}&steamids={id}"

            if not response:
                raise print(f"{self.prefix} {Fore.RED}An error occurred while getting the information...")
            else:
                result = json.loads(requests.get(response).text)

                if "response" in result and "players" in result["response"] and result["response"]["players"]:
                    steam_username = result["response"]["players"][0].get("personaname", "")
                else:
                    steam_username = "Loading nickname..."

                if "response" in result and "players" in result["response"] and result["response"]["players"]:
                    receivedAvatar = result["response"]["players"][0].get("avatarfull", "")
                else:
                    receivedAvatar = self.unknownAvatar

                allowedExtensions = ["jpg", "jpeg", "png"]
                urlExt = os.path.splitext(receivedAvatar)[1][1:].lower()

                if urlExt in allowedExtensions:
                    steam_avatar = receivedAvatar
                else:
                    steam_avatar = self.unknownAvatar

                if not steam_username:
                    steam_username = "Loading nickname..."

                data = {
                    "username": steam_username,
                    "avatar": steam_avatar,
                    "update": currentTimestamp,
                }

                dataEncode = json.dumps(data)

                if not dataEncode:
                    return print(f"{self.prefix} {Fore.RED}An error occurred while encoding the JSON data...{Fore.RESET}")
                else:
                    with open(file, "w") as f:
                        f.write(dataEncode)

                print(f"{self.prefix} SteamID {Fore.CYAN}{id}{Fore.RESET} was successfully cached.")

        else:
            self.updateCache(id)

    """
    
    Updates the cached data for a specific Steam ID by fetching the latest information from the Steam API.
    @param id: The Steam ID of the user to update.
    
    """
    def updateCache(self, id):
        file = f"{os.getcwd()}/data/{id}.json"
        currentTimestamp = int(time.time())
        print(f"{self.prefix} {Fore.GREEN}Updating{Fore.RESET} data from SteamID: {Fore.CYAN}{id}{Fore.RESET}")

        with open(file, "r") as f:
            json_data = f.read()

        json_obj = json.loads(json_data)

        interval = (currentTimestamp - json_obj["update"]) / 86400

        if interval >= 2:
            response = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={self.API_KEY}&steamids={id}"
            if not response:
                return print(f"{self.prefix} {Fore.RED}Invalid URL for the Steam API...{Fore.RESET}")

            result = json.loads(requests.get(response).text)

            if "response" in result and "players" in result["response"] and result["response"]["players"]:
                steam_username = result["response"]["players"][0].get("personaname", "")
            else:
                steam_username = "Loading nickname..."

            if "response" in result and "players" in result["response"] and result["response"]["players"]:
                receivedAvatar = result["response"]["players"][0].get("avatarfull", "")
            else:
                receivedAvatar = self.unknownAvatar

            allowedExtensions = ["jpg", "jpeg", "png"]
            urlExt = os.path.splitext(receivedAvatar)[1][1:].lower()

            if urlExt in allowedExtensions:
                steam_avatar = receivedAvatar
            else:
                steam_avatar = self.unknownAvatar

            if not steam_username:
                steam_username = "Loading nickname..."

            data = {
                "username": steam_username,
                "avatar": steam_avatar,
                "update": currentTimestamp,
            }

            dataEncode = json.dumps(data)

            if not dataEncode:
                return print(f"{self.prefix} {Fore.RED}An error occurred while encoding the JSON data...{Fore.RESET}")
            else:
                with open(file, "w") as f:
                    f.write(dataEncode)
            
            print(f"{self.prefix} SteamID {Fore.CYAN}{id}{Fore.RESET} was updated successfully")

    """
    
    Updates all cached users by fetching their latest data from the Steam API.
    This method only processes cached Steam IDs in chunks of 100 to comply with API limits.
    
    """
    def updateCachedUsers(self):
        start_time = time.time()
        print(f"{self.prefix} {Fore.GREEN}Updating cached users...{Fore.RESET}")
        data_list_folder = f"{os.getcwd()}/data"
        cached_ids = os.listdir(data_list_folder)

        if len(cached_ids) == 0:
            print(f"{self.prefix} {Fore.YELLOW}No cached users found.{Fore.RESET}")
            return

        print(f"{self.prefix} {Fore.YELLOW}Total cached users: {len(cached_ids)}{Fore.RESET}")

        # Split Steam IDs into chunks of 100
        steamid_chunks = [cached_ids[i:i+100] for i in range(0, len(cached_ids), 100)]

        for chunk in steamid_chunks:
            steamids = ",".join(chunk)
            response = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={self.API_KEY}&steamids={steamids}"

            if not response:
                print(f"{self.prefix} {Fore.RED}Invalid URL for the Steam API...{Fore.RESET}")
                continue

            result = json.loads(requests.get(response).text)

            if "response" in result and "players" in result["response"]:
                players_data = result["response"]["players"]

                i = 1

                for player_data in players_data:
                    if self.debug:
                        print(f"{self.prefix} {Fore.GREEN}Updating{Fore.RESET} user #{i}...")
                        
                    steam_id = player_data.get("steamid", "")
                    file = f"{os.getcwd()}/data/{steam_id}.json"
                    current_timestamp = int(time.time())

                    if os.path.exists(file):
                        with open(file, "r") as f:
                            json_data = f.read()

                        json_obj = json.loads(json_data)
                        json_obj["username"] = player_data.get("personaname", json_obj["username"])
                        json_obj["avatar"] = player_data.get("avatarfull", json_obj["avatar"])
                        json_obj["update"] = current_timestamp

                        data_encode = json.dumps(json_obj)

                        if not data_encode:
                            print(f"{self.prefix} {Fore.RED}An error occurred while encoding the JSON data for SteamID: {steam_id}{Fore.RESET}")
                            continue

                        with open(file, "w") as f:
                            f.write(data_encode)

                        end_time = time.time()
                        execution_time = end_time - start_time

                        print(f"{self.prefix} SteamID {Fore.CYAN}{steam_id}{Fore.RESET} was updated successfully {Fore.GREEN}[{Fore.CYAN}{execution_time} {Fore.GREEN}seconds]{Fore.RESET}")
                    else:
                        print(f"{self.prefix} {Fore.RED}File not found for SteamID: {steam_id}")

                    i += 1

        end_time = time.time()
        execution_time = end_time - start_time

        print(f"{self.prefix} {Fore.GREEN}Update completed in {Fore.CYAN}{execution_time}{Fore.GREEN} seconds.{Fore.RESET}")


"""

NOTE: This is an example usage, if you want to cache a new user, uncomment the input lines and run the script.

"""
steam = SteamCacheSystem()
steamid = input(f"{steam.prefix} SteamID:")
steam.cacheUser(steamid)
# steam.updateCachedUsers() <-- Uncomment this line to update all cached users
# steam.updateCache(steamid) <-- Uncomment this line to update a specific cached user
print(Fore.RESET)