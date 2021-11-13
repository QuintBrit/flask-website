'''This program finds products with the biggest difference between buy and sell offers and ranks them by most profit.
If I have time I will also include profit % and order filling speed.'''
import re

import requests, HTML, json, os, base64, tabulate, json2html
from git import Repo
from dotenv import load_dotenv

load_dotenv()

apiKey = os.environ.get("apikey")


def bazaar_flipper():
    bazaar_webpage = requests.get("https://api.slothpixel.me/api/skyblock/bazaar/")
    bazaar_data = json.loads(bazaar_webpage.text)  # acquiring data from api
    products = list(requests.get("https://api.hypixel.net/skyblock/bazaar?key=" + apiKey).json()[
                        "products"].keys())  # collects products from api
    default_values = {"Item": "", "Id": "", "Product Margin": 0, "Profit %": 0, "Buy Price": 0, "Sell Price": 0}
    final_products = {}
    final_products["item_name"] = {}
    final_products["id"] = {}
    final_products["buy_order_price"] = {}
    final_products["sell_order_price"] = {}
    final_products["product_margins"] = {}
    final_products["profit_percentage"] = {}
    # initialising variables

    products.remove("ENCHANTED_CARROT_ON_A_STICK")
    products.remove("BAZAAR_COOKIE")


    for i in range(len(products)):
        current_product = products[i]
        final_products["item_name"][i] = remove_formatting(id_to_name(current_product))
        final_products["id"][i] = current_product
        final_products["buy_order_price"][i] = bazaar_data[current_product]["buy_summary"][0]["pricePerUnit"]  # finds lowest buy price
        final_products["sell_order_price"][i] = bazaar_data[current_product]["sell_summary"][0]["pricePerUnit"]  # finds highest sell price
        product_margins = float(round((final_products["buy_order_price"][i] - final_products["sell_order_price"][i]), 1))  # calculates margin
        profit_percentage = round(product_margins / final_products["buy_order_price"][i], 2)  # calculates % profit
        final_products["product_margins"][i] = "{:,}".format(product_margins)  # adds commas
        final_products["profit_percentage"][i] = "{:,}".format(profit_percentage)  # adds commas

    desired_order_list = ["item_name", "id", "product_margins", "profit_percentage", "buy_order_price", "sell_order_price"]
    reordered_final_products = {k: final_products[k] for k in desired_order_list}
    # for i in range(len(products)):
    #
    print(reordered_final_products)
    return reordered_final_products


def build_table(table_data, path):
    HTMLFILE = path  # sets the file
    f = open(HTMLFILE, 'w+')  # opens the file
    table_attributes = '"class": "table table-striped" border="1" style="border: 1px solid #000000; border-collapse: collapse;" cellpadding="4" id="data"'
    htmlcode = json2html.json2html.convert(json=table_data, table_attributes=table_attributes) # transforms it into a table with module magic
    f.write(htmlcode)  # writes the table to the file


def isVanilla(pItem):
    vanilla_items = ["WOOD_AXE", "WOOD_HOE", "WOOD_PICKAXE", "WOOD_SPADE", "WOOD_SWORD", "GOLD_AXE", "GOLD_HOE",
                     "GOLD_PICKAXE", "GOLD_SPADE", "GOLD_SWORD", "ROOKIE_HOE"]  # hardcoded vanilla items
    filename = pItem + ".json"  # attaches .json to the filename so it is processed correctly
    for root, dir, files in os.walk(".\\neu-repo\\items"):  # loops through directory
        if filename in files:
            current_item = open(".\\neu-repo\\items\\" + filename, "r", encoding="utf-8", )
            current_item = json.loads(current_item.read())
            if pItem in vanilla_items:  # checks if in hardcoded vanilla items
                return True
            elif 'vanilla' in current_item:  # checks if they have 'vanilla' in file
                return True
            else:
                return False


def render_item(itemname):
    head = "https://sky.shiiyu.moe/item/".format(itemname)  # uses the sky.shiiyu api to render heads for me.
    return head


def isBazaarable(itemname):
    products = list(requests.get("https://api.hypixel.net/skyblock/bazaar?key=" + apiKey).json()[
                        "products"].keys())  # collects products from api
    if itemname in products:  # checks if product is in the list of bazaar products
        return True


def get_lowest_bin(itemname):
    data = requests.get(f"https://sky.coflnet.com/api/item/price/{itemname}/bin/").json()
    return data["lowest"]


def get_recipe(itemname):
    recipe_ids = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
    current_item_recipe = []
    item_path = "./neu-repo/items/{}".format(itemname)
    current_item = open(item_path, "r", encoding="utf-8")
    current_item = json.loads(current_item.read())
    for i in range(9):
        current_item_recipe.append(current_item["recipe"][f"{recipe_ids[i]}"])

    return current_item_recipe


def total_bazaar_price(itemname):
    total_price_array = []
    total_price = 0
    bazaar_webpage = requests.get("https://api.slothpixel.me/api/skyblock/bazaar/")
    bazaar_data = json.loads(bazaar_webpage.text)

    current_item_recipe = get_recipe(itemname)

    for i in range(9):
        head, sep, tail = current_item_recipe[i].partition(":")
        if current_item_recipe[i] != "":
            total_price_array.append(float(bazaar_data[head]["buy_summary"][0]["pricePerUnit"]) * float(
                current_item_recipe[i][-2] + current_item_recipe[i][-1]))
        else:
            total_price_array.append(0)

    for i in range(9):
        total_price += total_price_array[i]

    return total_price


def bazaar_tier_up(itemname):
    bazaar_webpage = requests.get("https://api.slothpixel.me/api/skyblock/bazaar/")
    bazaar_data = json.loads(bazaar_webpage.text)

    profit = bazaar_data[itemname]["sell_summary"][0]["pricePerUnit"] - total_bazaar_price(itemname)
    if profit > 0:
        return profit
    else:
        return ""


def craft_flipper():
    flips = requests.get(f"https://sky.coflnet.com/api/craft/profit/").json()
    flips["profit"] = flips["sellPrice"] - flips["craftCost"]
    flips["%profit"] = flips["profit"] / flips["craftCost"]
    return flips


def name_to_id(itemname):
    items = requests.get("https://api.hypixel.net/resources/skyblock/items")
    items = json.loads(items.text)
    for item in items["items"]:
        if item["name"] == itemname:
            return item["id"]


def id_to_name(itemname):
    items = requests.get("https://api.hypixel.net/resources/skyblock/items")
    items = json.loads(items.text)
    for item in items["items"]:
        if item["id"] == itemname:
            return item["name"]


def remove_formatting(string):
    formatting_codes = ["§4", "§c", "§6", "§e", "§2", "§a", "§b", "§3", "§1", "§9", "§d", "§5", "§f", "§7", "§8", "§0",
                        "§k", "§l", "§m", "§n", "§o", "§r"]  # sets up formatting codes so I can ignore them
    for i in range(len(formatting_codes)):
        string = string.replace("{}".format(formatting_codes[i]), "")  # as above
    return string


def worth_recombing():
    playername = input("What is your username? \n")
    profile = input("What is your profile called? \n")
    next_accessory = input(
        "What is the next accessory you're going for? \n(You may wish to use clowns' spreadsheet: https://docs.google.com/spreadsheets/d/1cPNax1xoN_VP015ggfEeKfNsDuqrRcqTBNq73HoOVqU/edit#gid=1494351710) \n")
    next_accessory_price = int(input("How much does it cost? \n"))
    next_accessory_id = name_to_id(next_accessory)
    reforge_stats = [1, 2, 3, 5, 8, 12]  # shows the str given from reforging to strong/level
    recomb_price = requests.get("https://api.slothpixel.me/api/skyblock/bazaar/RECOMBOBULATOR_3000")
    recomb_price = json.loads(recomb_price.text)
    recomb_price = recomb_price["buy_summary"][0]["pricePerUnit"]

    next_accessory_path = next_accessory_id + ".json"
    item_path = "./neu-repo/items/{}".format(next_accessory_path)
    next_accessory_file = open(item_path, "r", encoding="utf-8")
    next_accessory_lore = json.loads(next_accessory_file.read())
    next_accessory_lore = next_accessory_lore["lore"]
    # next_accessory_price = get_lowest_bin(next_accessory_id, False)

    if "COMMON" in next_accessory_lore:
        next_accessory_reforge_stats = reforge_stats[0]
        next_accessory_price_per_stats = next_accessory_reforge_stats / next_accessory_price
    elif "UNCOMMON" in next_accessory_lore:
        next_accessory_reforge_stats = reforge_stats[1]
        next_accessory_price_per_stats = next_accessory_reforge_stats / next_accessory_price
    elif "RARE" in next_accessory_lore:
        next_accessory_reforge_stats = reforge_stats[2]
        next_accessory_price_per_stats = next_accessory_reforge_stats / next_accessory_price
    elif "EPIC" in next_accessory_lore:
        next_accessory_reforge_stats = reforge_stats[3]
        next_accessory_price_per_stats = next_accessory_reforge_stats / next_accessory_price
    elif "LEGENDARY" in next_accessory_lore:
        next_accessory_reforge_stats = reforge_stats[4]
        next_accessory_price_per_stats = next_accessory_reforge_stats / next_accessory_price

    profile_data = requests.get(f"https://api.slothpixel.me/api/skyblock/profile/{playername}/{profile}")
    profile_data = json.loads(profile_data.text)
    accessories = profile_data["talisman_bag"]
    highest_current_accessory = accessories[0]
    if highest_current_accessory["rarity"] == "common":
        highest_current_accessory_upgraded_reforge_stats = reforge_stats[1] - reforge_stats[0]
        highest_current_accessory_upgraded_price_per_stats = highest_current_accessory_upgraded_reforge_stats / recomb_price
    elif highest_current_accessory["rarity"] == "uncommon":
        highest_current_accessory_upgraded_reforge_stats = reforge_stats[2] - reforge_stats[1]
        highest_current_accessory_upgraded_price_per_stats = highest_current_accessory_upgraded_reforge_stats / recomb_price
    elif highest_current_accessory["rarity"] == "rare":
        highest_current_accessory_upgraded_reforge_stats = reforge_stats[3] - reforge_stats[2]
        highest_current_accessory_upgraded_price_per_stats = highest_current_accessory_upgraded_reforge_stats / recomb_price
    elif highest_current_accessory["rarity"] == "epic":
        highest_current_accessory_upgraded_reforge_stats = reforge_stats[4] - reforge_stats[3]
        highest_current_accessory_upgraded_price_per_stats = highest_current_accessory_upgraded_reforge_stats / recomb_price
    elif highest_current_accessory["rarity"] == "legendary":
        highest_current_accessory_upgraded_reforge_stats = reforge_stats[5] - reforge_stats[4]
        highest_current_accessory_upgraded_price_per_stats = highest_current_accessory_upgraded_reforge_stats / recomb_price

    if next_accessory_price_per_stats > highest_current_accessory_upgraded_price_per_stats:
        print(f"Buy the {next_accessory}!")
        return False
    elif next_accessory_price_per_stats == highest_current_accessory_upgraded_price_per_stats:
        print(f"Buy the {next_accessory}")
        return False
    else:
        print(f"Recombobulate your {remove_formatting(highest_current_accessory['name'])}")
        return True




# ----------------------------------------------------------------------------------------------------------------------
# main

# Repo.clone_from("https://github.com/Moulberry/NotEnoughUpdates-REPO.git", "./neu-repo/")
# craft_flipper()
# worth_recombing()
# build_table(bazaar_flipper(), "./templates/flipper_data.html")
