import requests
import re
import time
import datetime
import websocket
import threading
import uuid
DEBUG_MODE = True

avalible_url = "knifex.skin"  # Обновляй тут url
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
            if DEBUG_MODE:
                print(request.status_code)
            if DEBUG_MODE:
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


def knifexSoket():
    print("Knifex start...")
    def on_message(ws, message):
        if DEBUG_MODE:
            print(message)
        applyMessage(message)

    def onOpen(ws):
        ws.send('422["join",{"ott":"' + str(uuid.uuid4()) + '"}]')
        def ping():
             while True:
                 time.sleep(25)
                 ws.send("2")
                 
        pingThread = threading.Thread(target=ping)
        pingThread.start()

    def on_close(ws, _, __):
        print("### closed Knife ###")
        knifexInit()
        print("### Auto open Knife ###")

    def on_error(ws, error):
        print("////////////////////////// ERROR KNIFE ///////////////////////////")
        knifexInit()
        print("### Auto open Knife ###")

    ws = websocket.WebSocketApp("wss://" + avalible_url + ":2083/socket.io/?EIO=3&transport=websocket",
                                on_message=on_message,
                                on_close=on_close,
                                on_error=on_error,
                                on_open=onOpen)

    ws.run_forever()


def twtchSokets(channelName):
    print("Twitch " + channelName + " started...")

    def on_message(ws, message):
        if DEBUG_MODE:
            print(message)
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
                 time.sleep(30)
                 ws.send("PING")

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
    twichThread.start()


def knifexInit():
    knifexThread = threading.Thread(target=knifexSoket)
    knifexThread.start()

knifexInit()


