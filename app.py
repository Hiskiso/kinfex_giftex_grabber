import requests
import re
import time
import datetime
import websocket
import threading
import uuid
import sys
import json


DEBUG_MODE_KNIFE = False
DEBUG_MODE_TWITCH = False

if len(sys.argv)>1:
    if sys.argv[1] == "-debugK":
        DEBUG_MODE_KNIFE =  True
    if sys.argv[1] == "-debugT":
        DEBUG_MODE_TWITCH =  True

avalible_url = "knifex.top"  # Обновляй тут url
twich_names = ["", ""]  # Тут названия каналов твича
accounts = ["526584f8-3aa6-4761-982e-c3d65891066a", ""]  # тут айди


def joinGiftex(link, message):
    good_count = 0
    nickname = ""
    reegx = [s for s in re.findall(r'display-name=(\w*)', message)]
    if len(reegx) > 0:
        nickname = reegx[0]
    print("https://" + avalible_url +
          '/pages/competitive/' + link + " " + nickname)
    for meta_data in accounts:
        request = requests.post("https://" + avalible_url + "/api/user/freebie/joinCompetitive/" + link, headers={
                                "content-type": "application/json", "meta-data": meta_data, "cookie": "id=" + meta_data+";"})
        if request.status_code == 200:
            response = request.json()
            if response["ok"] != False:
                print("[" + str(datetime.datetime.now().time()) + "](" + meta_data[:3] +
                      "..." + meta_data[len(meta_data)-3:len(meta_data)] + ") - \033[32mOK\033[0m")
                good_count += 1
            else:
                print("[" + str(datetime.datetime.now().time()) + "](" + meta_data[:3] + "..." +
                      meta_data[len(meta_data)-3:len(meta_data)] + ") - \033[31mНе ок((\033[0m")
        else:
            print("[" + str(datetime.datetime.now().time()) + "](" + meta_data[:3] + "..." +
                  meta_data[len(meta_data)-3:len(meta_data)] + ") - \033[31mUUID аккаунта неверный\033[0m")
            if DEBUG_MODE_KNIFE or DEBUG_MODE_TWITCH:
                print(request.status_code)
            if DEBUG_MODE_KNIFE or DEBUG_MODE_TWITCH:
                print(request.headers)

    print(str(good_count)+"/"+str(len(accounts)))


def applyMessage(message):
    regexp = [s for s in re.findall(
        r'knifex\.\w*/pages/competitive/\d{13}', message)]
    if len(regexp) > 0:
        competitiveId = [s for s in re.findall(r'\d{13}', regexp[0])]
        joinGiftex(competitiveId[0], message)
        
    if "giftex_emit" in message:
        regexp = [s for s in re.findall(
            r'\"link\":\"\d{13}\"', message)]
        competitiveId = [s for s in re.findall(r'\d{13}', regexp[0])]
        joinGiftex(competitiveId[0], message)
    if "pvp_fi" in message:
        jsonMessage = json.JSONDecoder().decode(message[2:])
        winners = ", ".join([str(winner) for winner in jsonMessage[1]["winners"]])
        print(f'Competitive id: {str(jsonMessage[1]["gameId"])} winners: {winners}')


def knifexSoket():
    print("Knifex start...")
    def on_message(ws, message):
        if DEBUG_MODE_KNIFE:
            print(message[0:150])
        applyMessage(message)

    def onOpen(ws):
        ws.send('422["join",{"ott":null}]')
        ws.send('421["joy",{"rm":"pvpcomp"}]')
        def ping():
             while ws.keep_running:
                time.sleep(25)
                if ws.keep_running:
                    ws.send("2")
                else:
                    ws.close()
        pingThread = threading.Thread(target=ping)
        pingThread.start()

    def on_close(ws, _, __):
        print("### closed Knife ###")
        knifexInit()
        print("### Auto open Knife ###")

    def on_error(ws, error):
        print("////////////////////////// ERROR KNIFE ///////////////////////////")
        knifexInit()
        print(error)
        print("### Auto open Knife ###")

    ws = websocket.WebSocketApp("wss://" + avalible_url + "/socket/sock2/?EIO=3&transport=websocket",
                                on_message=on_message,
                                on_close=on_close,
                                on_error=on_error,
                                on_open=onOpen)

    ws.run_forever()
    

def twtchSokets(channelName):
    print("Twitch " + channelName + " started...")

    def on_message(ws, message):
        if DEBUG_MODE_TWITCH:
            print(message[0:150])
        applyMessage(message)
        if "PING" in message:
            ws.send("PONG")

    def onOpen(ws):
        ws.send('CAP REQ :twitch.tv/tags twitch.tv/commands')
        ws.send('PASS SCHMOOPIIE')
        ws.send('NICK justinfan10764')
        ws.send('USER justinfan10764 8 * :justinfan10764')
        ws.send('JOIN #' + channelName)
      
        def ping():
             while True:
                ws.send("PING")
                time.sleep(30)

        pingThread = threading.Thread(target=ping)
        pingThread.start()

    def on_close(ws, _, __):

        print("### closed Twitch ###")

    def on_error(ws, error):
        print(error)
        print("### Error Twitch###")

    ws = websocket.WebSocketApp("wss://irc-ws.chat.twitch.tv/",
                                on_message=on_message,
                                on_close=on_close,
                                on_error=on_error,
                                on_open=onOpen)

    ws.run_forever()


for channel in twich_names:
    twichThread = threading.Thread(target=twtchSokets, args=[channel])
    # twichThread.start()


def knifexInit():
    knifexThread = threading.Thread(target=knifexSoket)
    knifexThread.start()

knifexInit()


