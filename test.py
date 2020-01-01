import json
import time
import datetime
import os

INF = 1000000


def unicode_convert(input):
    if isinstance(input, dict):
        return {unicode_convert(key): unicode_convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [unicode_convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def json_has_key(json, key):
    if key in json:
        return True
    else:
        return False


def addToDict2(thedict, key_a, key_b, val):
    if key_a in thedict:
        thedict[key_a].update({key_b: val})
    else:
        thedict.update({key_a: {key_b: val}})


def addToDict3(thedict, key_b, key_c, val):
    if key_b in thedict[key_b]:
        thedict[key_b].update({key_c: val})
    else:
        thedict.update({key_b: {key_c: val}})


def reqpos(context):
    for key in transfer_thre_json:
        if type(key) == int and transfer_thre_json[key]["participating"] == 1:
            print("[reqpos] main_account type:" + transfer_thre_json[key]["main_account"]["account_type"])
            print("[reqpos] main_account name:" + transfer_thre_json[key]["main_account"]["account_name"])
            context.req_pos(source=key,
                            # req_pos(main account)
                            account_type=transfer_thre_json[key]["main_account"]["account_type"],
                            account_name=transfer_thre_json[key]["main_account"]["account_name"])
            for cur in transfer_thre_json[key]["lower_threshold"]:
                for acc in transfer_thre_json[key][cur]["default_account"]:
                    print("[reqpos] account type:" + acc["account_type"])
                    print("[reqpos] account name:" + acc["account_name"])
                    context.req_pos(source=key,
                                    # req_pos cur deafult_account
                                    account_type=acc["account_type"],
                                    account_name=acc["account_name"])
    context.insert_func_after_c(x=freq, y=reqpos)


def reqhistory(context):
    print("[reqhistory]")
    t = time.time()
    now_time = "%d" % (t * 1000)
    print("query time : " + now_time)
    for wh in withdraw_history:
        print(type(wh["source"]), type(wh["cur"]), type(wh["start_time"]), type(now_time))
        print("query_what_history is {0}".format(query_what_history))
        if query_what_history == 0:
            context.transfer_history(
                source=wh["source"],
                flag=True,
                currency=wh["cur"],
                status=1,
                start_Time=wh["start_time"],
                end_Time=now_time,
                from_id=""
            )
        else:
            context.transfer_history(
                source=wh["to_source"],
                flag=False,
                currency=wh["cur"],
                status=1,
                start_Time=wh["start_time"],
                end_Time=now_time,
                from_id=""
            )
    # drive_withdraw(test_withdraw_count - 1)
    context.insert_func_after_c(x=freq, y=reqhistory)


# every freq,call reqpos once
def initialize(context):
    '''
    change transfer_threshold.json format
    {
  "balance_check_freq_ms": 10000,
  "batch_vol": {
    "xrp": 75,
    "pax": 2500,
    "tusd": 2500,
    "btc": 0.5,
    "eos": 1000
  },
  32: {
    "exchange_name": "Kucoin",
    "source": 32,
    "account_list": {
      "master-main": "master-main",
      "master-trade": "master-trade",
      "sub-main": "Sinodanish3-main",
      "sub-trade": "Sinodanish3-trade"
    },
    "default_account": { "xrp": "master-trade" },
    "lower_threshold": { "xrp": 300 },
    "upper_threshold": {
      "xrp": 300,
      "pax": 27500,
      "tusd": 27500,
      "btc": 5.5,
      "eos": 7000
    },
    "participating": 1,
    "main_account": {
      "account_type": "master-main",
      "account_name": "master-main"
    },
    "xrp": {
      "lower_threshold": 300,
      "upper_threshold": 300,
      "default_account": {
        "account_type": "master-trade",
        "account_name": "master-trade"
      }
    }
  }
}
    '''
    global visited
    visited = {}
    global road
    road = {}

    global graph
    graph = {}

    pathT = "./transfer_threshold_sample.json"
    file_transfer = open(pathT, "r")
    tt = file_transfer.read()
    json_data = json.loads(tt)
    global transfer_thre_json
    transfer_thre_json = {}
    global trans_account
    trans_account = {}
    global test_withdraw_count
    test_withdraw_count = 0
    global transfer_list
    transfer_list = []

    global withdraw_history
    withdraw_history = []

    global query_what_history
    query_what_history = 0  # 0 is withdraw history; 1 is deposit history

    transfer_thre_json["balance_check_freq_ms"] = json_data["balance_check_freq_ms"]
    # transfer_thre_json["batch_vol"]=json_data["batch_vol"]
    for exchange in json_data["exchange"]:
        transfer_thre_json[exchange["source"]] = {}
        transfer_thre_json[exchange["source"]] = exchange
        transfer_thre_json[exchange["source"]]["main_account"] = {}
        transfer_thre_json[exchange["source"]]["main_account"]["account_type"] = exchange["account_list"][0][
            "account_type"]
        transfer_thre_json[exchange["source"]]["main_account"]["account_name"] = exchange["account_list"][0][
            "account_name"]

        for cur in exchange["lower_threshold"]:
            transfer_thre_json[exchange["source"]][cur] = {}
            transfer_thre_json[exchange["source"]][cur]["lower_threshold"] = exchange["lower_threshold"][cur]
            transfer_thre_json[exchange["source"]][cur]["standard_volume"] = exchange["standard_volume"][cur]
            transfer_thre_json[exchange["source"]][cur]["default_account"] = []
            deafult_account_ID = exchange["default_account"][cur]
            if not trans_account.has_key(cur):
                trans_account[cur] = []
            account_temp = {}
            account_temp["valid"] = False
            account_temp["source"] = exchange["source"]
            account_temp["transfer_vol"] = 0
            account_temp["on_treading_vol"] = 0
            account_temp["account_name"] = account_temp["account_type"] = ""
            for i in exchange["account_list"]:
                for acc in deafult_account_ID:
                    if i["ID"] == acc:
                        temp_acc = {}
                        temp_acc["ID"] = acc
                        temp_acc["account_name"] = i["account_name"]
                        temp_acc["account_type"] = i["account_type"]
                        transfer_thre_json[exchange["source"]][cur]["default_account"].append(temp_acc)
                        account_temp["account_name"] = i["account_name"]
                        account_temp["account_type"] = i["account_type"]
                        account_temp["ID"] = acc
                        trans_account[cur].append(account_temp.copy())
                        print("[initialize] trans_account[cur] add one default account :" + account_temp[
                            "ID"] + ",cur " + cur + "source " + str(exchange["source"]))
    transfer_thre_json = unicode_convert(transfer_thre_json)
    trans_account = unicode_convert(trans_account)

    for exchange in json_data["exchange"]:
        get_graph(exchange["source"])
        floyd(exchange["source"])

    global freq
    freq = transfer_thre_json["balance_check_freq_ms"] / 1000

    print("[initialize] freq is :" + str(freq))
    '''
    change Destination_address.json format
    {
        32: {
          "exchange": "Kucoin",
          "account_name": "sf_beavo",
          "source": 32,
          "WithdrawWhiteLists": {
            "btc": [ "375e6Hz5PEoC4AFZEq16a8naM9mKUDyDRS", "" ],
            "xrp": [ "rUW9toSjQkLY6EspdnBJP2paG4hWKmNbMh", "1862094677" ]
          }
        }
    }

    '''
    pathD = "./Destination_Address.json"
    file_destin = open(pathD, "r")
    da = file_destin.read()
    json_data = json.loads(da)
    file_destin.close()
    global destina_addr_json
    destina_addr_json = {}
    for dest in json_data["destination_address"]:
        destina_addr_json[dest["source"]] = dest
        print("[initialize] dest ")
    destina_addr_json = unicode_convert(destina_addr_json)

    # global max_balance
    # max_balance = {}
    # for cur in transfer_thre_json["batch_vol"]:
    # 	max_balance[cur] = 0

    global transfer_balance_sr
    transfer_balance_sr = {}

    global transferred_value
    transferred_value = {}
    for source in transfer_thre_json:
        if type(source) == int:
            for cur in transfer_thre_json[source]["lower_threshold"]:
                addToDict2(transferred_value, source, cur, 0)
                print("[initialize]lower_threshold:" + cur)

    # global batch_vol_amount
    # batch_vol_amount = {}
    # for bv in transfer_thre_json["batch_vol"]:
    # 	for key in transfer_thre_json:
    # 		if type(key)==int:
    # 			addToDict2(batch_vol_amount, bv,key, 0)

    for key in transfer_thre_json:
        if type(key) == int and transfer_thre_json[key]["participating"] == 1:
            context.add_td(source=key)
            print("[initialize] debug:")
    context.insert_func_after_c(x=freq, y=reqpos)
    context.insert_func_after_c(x=freq, y=reqhistory)
    # os.system("config=sell_it.conf wingchun strategy -p ./sell_it.py -n sell_it>sell.log")


def isFinishedQuery():
    global trans_account
    for cur in trans_account:
        for acc in trans_account[cur]:
            if acc["valid"] == False:
                print("[isFinishedQuery]: " + acc["ID"])
                return False
    return True


def clearQuery():
    global trans_account
    for cur in trans_account:
        for acc in trans_account[cur]:
            acc["valid"] = False


def clearVisited(source):
    global visited, transfer_thre_json
    for alist in transfer_thre_json[source]["account_list"]:
        visited[alist["ID"]] = False


def get_graph(source):
    global graph, transfer_thre_json
    graph[source] = {}
    for alist in transfer_thre_json[source]["account_list"]:
        graph[source][alist["ID"]] = {}
        trans_road = transfer_thre_json[source]["enable_transfer"][alist["account_type"]]
        for blist in transfer_thre_json[source]["account_list"]:
            graph[source][alist["ID"]][blist["ID"]] = {}
            graph[source][alist["ID"]][blist["ID"]]["road"] = []
            graph[source][alist["ID"]][blist["ID"]]["pre"] = ""
            graph[source][alist["ID"]][blist["ID"]]["dist"] = INF
            if (alist["ID"] == blist["ID"]):
                graph[source][alist["ID"]][blist["ID"]]["dist"] = 0
                graph[source][alist["ID"]][blist["ID"]]["pre"] = alist["ID"]
                continue
            if alist["account_name"] == blist["account_name"]:
                for aim_type in trans_road["self"]:
                    if aim_type == blist["account_type"]:
                        graph[source][alist["ID"]][blist["ID"]]["dist"] = 1
                        graph[source][alist["ID"]][blist["ID"]]["pre"] = alist["ID"]
                        print("{0} -1-> {1}".format(alist["ID"], blist["ID"]))
            else:
                for aim_type in trans_road["other"]:
                    if aim_type == blist["account_type"]:
                        graph[source][alist["ID"]][blist["ID"]]["dist"] = 1
                        graph[source][alist["ID"]][blist["ID"]]["pre"] = alist["ID"]
                        print("{0} -2-> {1}".format(alist["ID"], blist["ID"]))


def floyd(source):
    global graph, transfer_thre_json
    for alist in transfer_thre_json[source]["account_list"]:
        for blist in transfer_thre_json[source]["account_list"]:
            for clist in transfer_thre_json[source]["account_list"]:
                if graph[source][blist["ID"]][alist["ID"]]["dist"] + graph[source][alist["ID"]][clist["ID"]]["dist"] < \
                        graph[source][blist["ID"]][clist["ID"]]["dist"]:
                    graph[source][blist["ID"]][clist["ID"]]["dist"] = graph[source][blist["ID"]][alist["ID"]]["dist"] + \
                                                                      graph[source][alist["ID"]][clist["ID"]]["dist"]
                    graph[source][blist["ID"]][clist["ID"]]["pre"] = graph[source][alist["ID"]][clist["ID"]]["pre"]
    print(graph[source])
    for alist in transfer_thre_json[source]["account_list"]:
        for blist in transfer_thre_json[source]["account_list"]:
            if graph[source][alist["ID"]][blist["ID"]]["dist"] >= INF or graph[source][alist["ID"]][blist["ID"]][
                "dist"] == 0:
                continue
            graph[source][alist["ID"]][blist["ID"]]["road"].append(blist["ID"])
            preId = graph[source][alist["ID"]][blist["ID"]]["pre"]
            graph[source][alist["ID"]][blist["ID"]]["road"].append(preId)
            while preId != alist["ID"]:
                preId = graph[source][alist["ID"]][preId]["pre"]
                graph[source][alist["ID"]][blist["ID"]]["road"].append(preId)
            graph[source][alist["ID"]][blist["ID"]]["road"].reverse()
            print("[floyd] from {0} to {1}".format(alist["ID"], blist["ID"]) + str(
                graph[source][alist["ID"]][blist["ID"]]["road"]))


def getId(source, name, a_type):
    global transfer_thre_json
    for alist in transfer_thre_json[source]["account_list"]:
        if (alist["account_name"] == name and alist["account_type"] == a_type):
            print("[getId] id is" + alist["ID"])
            return alist["ID"]
    return ""


def getNameType(source, ID):
    global transfer_thre_json
    for alist in transfer_thre_json[source]["account_list"]:
        if (alist["ID"] == ID):
            return alist["account_name"], alist["account_type"]
    return ""


def getUpperAccount(cur, source):
    global trans_account, transfer_thre_json
    # print("[getUpperAccount]:")

    #  fee_transfer = transfer_thre_json[source]["transfer_minimum"][cur]*100000000

    sorted(trans_account[cur], key=lambda x: x["transfer_vol"] - x["on_treading_vol"], reverse=True)
    for acc in trans_account[cur]:
        if acc["source"] == source and acc["transfer_vol"] - abs(acc["on_treading_vol"]) > 0:
            print("[getUpperAccount] account_ID: " + acc["ID"] + " transfer_vol:" + str(acc["transfer_vol"]))
            return acc

    fee = transfer_thre_json[source]["withdrawal_minimum"][cur] * 100000000

    for acc in trans_account[cur]:
        if acc["source"] == source or acc["transfer_vol"] - acc["on_treading_vol"] <= fee:
            continue
        print("[getUpperAccount] other source account_ID: " + acc["ID"] + " transfer_vol:" + str(
            acc["transfer_vol"] - acc["on_treading_vol"]))
        return acc
    print("[getUpperAccount]: None")
    return None


def hardTrans(context):
    print(context.req_inner_transfer(
        source=16,
        currency="XRP",
        volume=5500 * 100000000,
        from_type="master-margin",
        from_name="Spencer.fan@beavoinvest.com",
        to_type="master-main",
        to_name="Spencer.fan@beavoinvest.com"))


def test_transfer(context, pos_handler):
    account_name = "spencer.fan@sino-danish.com"
    account_name2 = "Spencer.fan@beavoinvest.com"
    print("[test_transfer]: " + pos_handler.get_account_name())
    if pos_handler.get_account_name() == account_name or pos_handler.get_account_name() == account_name2:
        print("[test_transfer] type" + pos_handler.get_account_type() + " tot " + str(
            pos_handler.get_long_tot("XRP") / 100000000))
    else:
        return
    # context.req_inner_transfer(
    #     source=16,
    #     currency="XRP",
    #     volume=50 * 100000000,
    #     from_type="sub-main",
    #     from_name= account_name,
    #     to_type="sub-margin",
    #     to_name= account_name)


def on_pos(context, pos_handler, request_id, source, rcv_time):
    if request_id == -1:
        context.pos_set = False
        return
    # hardTrans(context)

    print(time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()))
    print(
        "*******************" + pos_handler.get_account_name() + "    " + pos_handler.get_account_type() + "*******************")
    test_transfer(context, pos_handler)
    # hardTrans(context)

    if (len(transfer_list) != 0):
        print("list is not null:" + str(transfer_list))
        return
    global transfer_thre_json, destina_addr_json, max_balance, transfer_balance_sr, transferred_value, mutex, trans_account
    if source in transfer_thre_json and transfer_thre_json[source]["participating"] == 1:  # source participat transfer

        for cur in transfer_thre_json[source]["lower_threshold"]:  # find which source cur value is biggests
            for account in trans_account[cur]:
                print("[on_pos]  pos_name is " + str(pos_handler.get_account_name()) + " source is " + str(
                    source) + " acount_name is " + account[
                          "account_name"] + " pos_type:" + pos_handler.get_account_type()
                      + " acount_type " + account["account_type"] + " source is " + str(account["source"]))

                if pos_handler.get_account_name() == account["account_name"] and pos_handler.get_account_type() == \
                        account["account_type"]:
                    print("[on_pos] 196: " + str(source) + "," + cur + " _default_account_balance: " + account[
                        "account_name"] + " " + str(
                        pos_handler.get_long_tot(cur) / 100000000) + " xuzeng " + str(account["on_treading_vol"]))
                    account["valid"] = True
                    print("[on_pos] get_long_tot: " + str(
                        pos_handler.get_long_tot(cur) / 100000000) + " [on_pos] account_name " + str(
                        account["account_name"]) + "  account_type: " + str(account["account_type"]) + " xuzeng " + str(
                        account["on_treading_vol"]))
                    if pos_handler.get_long_tot(cur) > transfer_thre_json[source][cur]["standard_volume"]:
                        account["transfer_vol"] = pos_handler.get_long_tot(cur) - transfer_thre_json[source][cur][
                            "standard_volume"] * 100000000 + account["on_treading_vol"]
                        print("[on_pos]  transfer_vol:" + str(account["transfer_vol"] / 100000000))
                    if account["on_treading_vol"] != 0:  # xuzeng not withdraw
                        return
        if not isFinishedQuery():
            print("[on_pos] Not finished query")
            return
        # return #if you only query the long_tots

        for cur in transfer_thre_json[source]["lower_threshold"]:  # transfer general logic
            for account in transfer_thre_json[source][cur]["default_account"]:
                if pos_handler.get_account_name() == account["account_name"] and pos_handler.get_account_type() == \
                        account["account_type"]:  # cur_max to lower main_account

                    if pos_handler.get_long_tot(cur) < transfer_thre_json[source]["lower_threshold"][cur] * 100000000:
                        # after transfer tv volume,cur value in source < lower_threshold
                        print("after transfer tv volume,cur value in source < lower_threshold")
                        # while (pos_handler.get_long_tot(cur) + batch_vol_amount[cur][source] * transfer_thre_json["batch_vol"][cur]
                        # 	   * 100000000 < transfer_thre_json[source]["lower_threshold"][cur] * 100000000):
                        # 		batch_vol_amount[cur][source] += 1
                        # find compatible transfer volume
                        upperAccount = getUpperAccount(cur, source)
                        if upperAccount == None:
                            return

                        if upperAccount["source"] in transfer_thre_json:
                            if source == upperAccount["source"]:
                                # the transfer account and the aim account is in the same source
                                print("[on_pos] aim account is in the same source with upperAccount")
                                print("[on_pos] find aim account cur in source: " + str(source))
                                print("[on_pos] trasnfer_vol[cur]:" + str(upperAccount["transfer_vol"] / 100000000))
                                flag = inner_transfer(context=context,
                                                      source=upperAccount["source"],
                                                      cur=cur,
                                                      volume=int(upperAccount["transfer_vol"]),
                                                      from_type=upperAccount["account_type"],
                                                      from_name=upperAccount["account_name"],
                                                      to_type=account["account_type"],
                                                      to_name=account["account_name"])
                                if (flag):
                                    upperAccount["transfer_vol"] = 0
                            else:
                                print("[on_pos] aim account is not in the same source with upperAccount")
                                print("[on_pos] upper source " + str(
                                    upperAccount["source"]) + ",and aim source is " + str(source))
                                print(
                                    "[on_pos] trasnfer_vol[cur]:" + str(
                                        upperAccount["transfer_vol"] / 100000000) + "[{0}]".format(
                                        cur))
                                print("[on_pos] address:" + destina_addr_json[source]["WithdrawWhiteLists"][cur][0])
                                print("[on_pos] tag:" + destina_addr_json[source]["WithdrawWhiteLists"][cur][1])
                                flag = withdraw(context=context,
                                                source=upperAccount["source"],
                                                cur=cur,
                                                volume=int(upperAccount["transfer_vol"]),
                                                from_type=upperAccount["account_type"],
                                                from_name=upperAccount["account_name"],
                                                to_source=source,
                                                to_type=account["account_type"],
                                                to_name=account["account_name"]
                                                )
                                if flag:
                                    upperAccount["transfer_vol"] = 0
        if not context.pos_set:
            context.data_wrapper.set_pos(pos_handler, source)


def on_transfer_history(context, transfer_history, request_id, source, rcv_time, is_Last, flag):
    global query_what_history
    if transfer_history.Status == 1:
        print("flag is {0}".format(flag))
        if flag == True:
            print("[on_transfer_history]: transfer_history" + str(transfer_history) + " From ID " + str(
                transfer_history.FromID) + "request_id: " + str(rcv_time) + " TxId is  " + str(transfer_history.TxId))
            for wit in withdraw_history:
                if wit["ID"] == transfer_history.FromID:
                    wit["TxId"] = str(transfer_history.TxId)
                    query_what_history = 1


        else:
            print("[on_transfer_history]: transfer_history" + " TxId " + str(transfer_history.TxId))
            for wit in withdraw_history:
                if transfer_history.FromID in wit["TxId"]:
                    res = finishWithdraw(wit)
                    query_what_history = 0
                    if not res:
                        print("[on_transfer_history] FINISH WITHDRAW ERROR")


def on_transfer(context, transfer, order_id, source, rcv_time):
    context.log_info("on_transfer")
    if order_id in transfer_list:
        transfer_list.remove(order_id)
    print('on_transfer', order_id)


def on_error(context, error_id, error_msg, request_id, source, rcv_time):
    context.log_error('on_error:' + " errorid: " + str(error_id) + " error_msg: " + error_msg)
    if request_id in transfer_list:
        transfer_list.remove(request_id)
    print('on_error:' + " errorid: " + str(error_id) + " error_msg: " + error_msg)


def on_withdraw(context, withdraw, order_id, source, rcv_time):
    print
    "----on withdraw----"
    context.log_info("----on withdraw----")
    context.log_info("transfer_money:" + str(withdraw.Volume) + "rcv_time:" + str(rcv_time))
    print("transfer_money:" + str(withdraw.Volume) + "rcv_time:" + str(rcv_time))
    print('----on withdraw----', order_id)
    for wit in withdraw_history:
        if order_id == wit["reqId"]:
            print("ID is" + str(withdraw.ID))
            wit["ID"] = withdraw.ID


def inner_transfer(context, source, cur, volume, from_type, from_name, to_type, to_name):
    print("\n[inner_transfer]")
    print("[inner_transfer] from " + from_type + " to " + to_type + " transfer " + str(volume))
    clearVisited(source)
    fromId = getId(source, from_name, from_type)
    toId = getId(source, to_name, to_type)
    road = graph[source][fromId][toId]["road"]
    if graph[source][fromId][toId]["dist"] >= INF:
        print("[inner_transfer] Not reach!")
        return False
    temp_from_entity = {}
    temp_from_entity["account_type"] = from_type
    temp_from_entity["account_name"] = from_name
    print(str(road))

    for temp_ID in road[1:]:
        temp_name, temp_type = getNameType(source, temp_ID)
        reqId = context.req_inner_transfer(
            source=source,
            currency=cur,
            volume=volume,
            from_type=temp_from_entity["account_type"],
            from_name=temp_from_entity["account_name"],
            to_type=temp_type,
            to_name=temp_name)
        print(reqId)
        print(" [inner_transfer]:successfully! from_name:" + temp_from_entity["account_name"] + ",from_type:" +
              temp_from_entity["account_type"] + ",to_name:" + temp_name + ",to_type:" + temp_type
              + " volume:" + str(volume))
        temp_from_entity["account_type"] = temp_type
        temp_from_entity["account_name"] = temp_name
        transfer_list.append(reqId)
        time.sleep(5)  # inner transfer time

    print(" successfully! source: " + str(source) + " inner_transfer: " + cur + "\n")
    return True


'''
to_source: aim source
'''


def withdraw(context, source, cur, volume, from_type, from_name, to_source, to_type, to_name):
    print(
        "[withdraw]  Transfer " + str(volume) + "from {0}:{1}:{2} to {3}:{4}:{5} ".format(source, from_name,
                                                                                          from_type,
                                                                                          to_source,
                                                                                          to_name, to_type))
    global transfer_thre_json, trans_account

    from_main_name = transfer_thre_json[source]["main_account"]["account_name"]
    from_main_type = transfer_thre_json[source]["main_account"]["account_type"]
    to_main_name = transfer_thre_json[to_source]["main_account"]["account_name"]
    to_main_type = transfer_thre_json[to_source]["main_account"]["account_type"]
    fee = transfer_thre_json[source]["transfer_fee"][cur] * 100000000
    if (from_name != transfer_thre_json[source]["main_account"]["account_name"] or from_type !=
            transfer_thre_json[source]["main_account"]["account_type"]):
        print("[withdraw] should transfer to main account")
        res = inner_transfer(context=context,
                             source=source,
                             cur=cur,
                             volume=volume,
                             from_type=from_type,
                             from_name=from_name,
                             to_type=from_main_type,
                             to_name=from_main_name)

        if not res:
            print("[withdraw] Transfer from " + from_name + "to" + from_main_type + "Failed")
            return False

    for cur1 in trans_account:
        for acc in trans_account[cur1]:
            if acc["account_name"] == to_name and acc["account_type"] == to_type:
                acc["on_treading_vol"] += volume

    reqId = context.withdraw_currency(source=source,
                                      currency=cur,
                                      volume=volume,
                                      address=destina_addr_json[to_source]["WithdrawWhiteLists"][cur][0],
                                      tag=destina_addr_json[to_source]["WithdrawWhiteLists"][cur][1])

    global withdraw_history

    temp_history = {}
    t = time.time()
    now_time = "%d" % (t * 1000)
    print("send_time: " + (now_time))
    temp_history["context"] = context
    temp_history["source"] = source
    temp_history["cur"] = cur
    temp_history["start_time"] = int(now_time)
    temp_history["address"] = destina_addr_json[source]["WithdrawWhiteLists"][cur][0]
    temp_history["to_source"] = to_source
    temp_history["volume"] = int(volume - fee)
    temp_history["reqId"] = reqId
    temp_history["from_name"] = from_name
    temp_history["from_type"] = from_type
    temp_history["to_main_name"] = to_main_name
    temp_history["to_main_type"] = to_main_type
    temp_history["to_name"] = to_name
    temp_history["to_type"] = to_type
    temp_history["ID"] = 0
    temp_history["TxId"] = ""
    # temp_history["delay"] =  transfer_thre_json[source]["deposit_receive_delay"]
    # print(temp_history)
    withdraw_history.append(temp_history.copy())

    return True
    # TODO: find history


# def test_drive_withdraw(order_id):
#     print('----drive_withdraw----', order_id)
#     for wit in withdraw_history:
#         if order_id == wit["reqId"]:
#             wit["ID"] = order_id + 10000
#             drive_withdraw_history(1, order_id + 10000)


def test_drive_withdraw_history(status, id):
    print("----on_transfer_history----")
    print(status)
    print(id)
    if status == 1:
        for wit in withdraw_history:
            print(wit["ID"])
            if wit["ID"] == id:
                # time.sleep(wit["delay"])
                res = finishWithdraw(wit)
                if not res:
                    print("[on_transfer_history] FINISH WITHDRAW ERROR")


def finishWithdraw(history_param):
    print("\n[finishWithdraw]")
    global trans_account
    for cur in trans_account:
        for acc in trans_account[cur]:
            if acc["account_name"] == history_param["to_name"] and acc["account_type"] == history_param["to_type"]:
                acc["on_treading_vol"] = 0  # remove the xuzeng

    print("outer_transfer: " + history_param["cur"] + str(history_param["volume"]) + " from: " + str(
        history_param["source"]) + " to: " + str(history_param["to_source"]))
    if history_param["to_main_name"] != history_param["to_name"] or history_param["to_main_type"] != history_param[
        "to_type"]:
        print("[withdraw] should transfer to sub account")
        print(type(history_param["context"]), type(history_param["to_source"]), type(history_param["cur"]),
              type(history_param["volume"]), type(history_param["to_main_name"]), type(history_param["to_main_type"]),
              type(history_param["to_type"]), type(history_param["to_name"]))
        res = inner_transfer(context=history_param["context"],
                             source=history_param["to_source"],
                             cur=history_param["cur"],
                             volume=history_param["volume"],
                             from_name=history_param["to_main_name"],
                             from_type=history_param["to_main_type"],
                             to_type=history_param["to_type"],
                             to_name=history_param["to_name"])
        if not res:
            print("[withdraw] Transfer from " + history_param["from_name"] + "to" + history_param["to_name"] + "Failed")
            return False

    withdraw_history.remove(history_param)
    print(history_param)
    return True

