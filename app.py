import requests
import re
import datetime
import websocket
import threading
import uuid
DEBUG_MODE = False

avalible_url = "knifex.skin"  # Обновляй тут url
twich_names = ['kaifarik0644', ""]  # Тут названия каналов твича
accounts = ["2ac9d5d3-f4d9-4b2f-a56a-f913740facaa", ""]  # тут айди


def joinGiftex(link):
    good_count = 0
    print("https://" + avalible_url +
          '/pages/competitive/' + link)
    for meta_data in accounts:
        request = requests.post("https://" + avalible_url + "/api/user/freebie/joinCompetitive/"+link, headers={
                                "content-type": "application/json", "meta-data": meta_data, "cookie": "id="+meta_data+";"})
        if request.status_code == 200:
            response = request.json()
            if response["ok"] != False:
                print("[" + str(datetime.datetime.now().time()) + "](" + meta_data[:3] +
                      "..." + meta_data[len(meta_data)-3:len(meta_data)] + ") - \033[32mOK\033[0m")
                good_count += 1
            else:
                print("[" + str(datetime.datetime.now().time()) + "](" + meta_data[:3] + "..." +
                      meta_data[len(meta_data)-3:len(meta_data)] + ") - \033[31mНе ок((\033[0m")
                print(request.json())
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
        joinGiftex(competitiveId[0])
        
    if "giftex_emit" in message:
        regexp = [s for s in re.findall(
            r'\"link\":\"\d{13}\"', message)]
        competitiveId = [s for s in re.findall(r'\d{13}', regexp[0])]
        joinGiftex(competitiveId[0])


def knifexSoket():
    print("Knifex started...")

    def set_interval(func, sec):
        def func_wrapper():
            set_interval(func, sec)
            func()
        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t

    def on_message(ws, message):
        if DEBUG_MODE:
            print(message)
        applyMessage(message)

    def onOpen(ws):
        def timeout():
            ws.send("2")
        set_interval(timeout, 25)
        ws.send('422["join",{"ott":"' + str(uuid.uuid4()) + '"}]')

    def on_close(ws, _, __):
        print("### closed Knife ###")

    def on_error(ws, error):
        print(error)
        print("### closed Knife ###")

    ws = websocket.WebSocketApp("wss://" + avalible_url + ":2053/socket.io/?EIO=3&transport=websocket",
                                on_message=on_message,
                                on_close=on_close,
                                on_error=on_error,
                                on_open=onOpen)

    ws.run_forever()


def twtchSokets(channelName):
    def set_interval(func, sec):
        def func_wrapper():
            set_interval(func, sec)
            func()
        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t

    print("Twitch " + channelName + " started...")

    def on_message(ws, message):
        if DEBUG_MODE:
            print(message)
        applyMessage(message)
        if "PING" in message:
            ws.send("PONG")

    def onOpen(ws):
        def ping():
            ws.send("PING")
        set_interval(ping, 300)
        ws.send('CAP REQ :twitch.tv/tags twitch.tv/commands')
        ws.send('PASS SCHMOOPIIE')
        ws.send('NICK justinfan10764')
        ws.send('USER justinfan10764 8 * :justinfan10764')
        ws.send('JOIN #' + channelName)

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


knifexThread = threading.Thread(target=knifexSoket)


knifexThread.start()
