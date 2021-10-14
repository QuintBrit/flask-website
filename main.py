'''This program finds products with the biggest difference between buy and sell offers and ranks them by most profit.
If I have time I will also include profit % and order filling speed.'''

import requests, HTML, json, os, re
from git import Repo
from dotenv import load_dotenv

load_dotenv()

apiKey = os.environ.get("apikey")
nestcount = 0


def bazaar_flipper():
    bazaar_webpage = requests.get("https://api.slothpixel.me/api/skyblock/bazaar/")
    bazaar_data = json.loads(bazaar_webpage.text)  # acquiring data from api
    bazaar_items = requests.get("https://api.hypixel.net/resources/skyblock/items")
    bazaar_items = json.loads(bazaar_items.text)

    products = list(requests.get("https://api.hypixel.net/skyblock/bazaar?key=" + apiKey).json()[
                        "products"].keys())  # collects products from api
    final_products = []
    buy_order_price = []
    sell_order_price = []
    product_margins = []
    profit_percentage = []
    item_names = []  # initialising variables

    products.remove("ENCHANTED_CARROT_ON_A_STICK")
    products.remove("BAZAAR_COOKIE")
    for i in range(len(bazaar_items["items"])):
        try:
            if bazaar_items["items"][i]["id"] == "ENCHANTED_CARROT_ON_A_STICK":
                bazaar_items["items"].pop(i)  # removes glitched products
        except IndexError:
            break

    for i in range(len(products)):
        buy_order_price.append(bazaar_data[products[i]]["buy_summary"][0]["pricePerUnit"])  # finds lowest buy price
        sell_order_price.append(bazaar_data[products[i]]["sell_summary"][0]["pricePerUnit"])  # finds highest sell price
        product_margins.append(round((buy_order_price[i] - sell_order_price[i]), 1))  # calculates margin
        profit_percentage.append(round(product_margins[i] / buy_order_price[i], 2))  # calculates % profit
        profit_percentage[i] = "{:,}".format(profit_percentage[i])
        product_margins[i] = "{:,}".format(product_margins[i])
        if bazaar_items["items"][i]["id"] == products[i]:
            item_names.append(bazaar_items["name"])

    final_products.append([item_names, products, product_margins, profit_percentage])  # combines the lists
    return final_products


def build_table(func, path, header_row):
    if func == 1:
        table_data = bazaar_flipper()
    HTMLFILE = path  # sets the file
    f = open(HTMLFILE, 'w+')  # opens the file

    htmlcode = HTML.table(table_data, header_row)  # transforms it into a table with module magic

    f.write(htmlcode)  # writes the table to the file

    t = open(path, "r+")
    replacement = t.read()
    replacement = replacement.replace(
        '<TABLE border="1" style="border: 1px solid #000000; border-collapse: collapse;" cellpadding="4"',
        '<TABLE class="table table-striped" border="1" style="border: 1px solid #000000; border-collapse: collapse;" cellpadding="4" id="data"')
    replacement = replacement.replace(
        '<TABLE class="table table-striped" border="1" style="border: 1px solid #000000; border-collapse: collapse;" cellpadding="4" id="data">',
        '<TABLE class="table table-striped" border="1" style="border: 1px solid #000000; border-collapse: collapse;" cellpadding="4" id="data">\n<thead>')
    replacement = replacement.replace(
        """<TH>Profit %</TH>
 </TR>""", """<TH>Profit %</TH>
 </TR>
</thead>"""
    )
    replacement = replacement.replace(
        '</TABLE>',
        '</tbody>\n</TABLE>')
    t.close()
    t = open(path, "w+")
    t.write(replacement)


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


def auction_declarations(itemname):
    formatting_codes = ["§4", "§c", "§6", "§e", "§2", "§a", "§b", "§3", "§1", "§9", "§d", "§5", "§f", "§7", "§8", "§0",
                        "§k", "§l", "§m", "§n", "§o", "§r"]  # sets up formatting codes so I can ignore them
    for i in range(len(formatting_codes)):
        itemname = itemname.replace("{}".format(formatting_codes[i]), "")  # as above
    itemname = itemname.lower()
    itemname = re.sub(r" ", '', itemname)
    current_item_auctions = list(requests.get(
        "https://hyskyapi.000webhostapp.com/apihandle.php?req=search&query=" + itemname).json())  # create a list of the current auctions from hysky api

    return current_item_auctions


def isAuctionable(itemname):
    if auction_declarations(
            itemname) != []:  # checks if there's any auctions for [item]. note this may break when encountering extremely rare items such as dctr's space helmet
        return True


def isBazaarable(itemname):
    products = list(requests.get("https://api.hypixel.net/skyblock/bazaar?key=" + apiKey).json()[
                        "products"].keys())  # collects products from api
    if itemname in products:  # checks if product is in the list of bazaar products
        return True


def get_lowest_bin(itemname, isBook):
    total_pages = 50  # test value, we'll see how it goes
    while True:
        if isBook == True:  # because hysky api is weird, you need to use /ebs to find books
            itemname = "/ebs%20" + itemname
            for page_num in range(total_pages):  # iterates through all pages of ah
                current_item_auctions = list(requests.get(
                    f"https://hyskyapi.000webhostapp.com/apihandle.php?req=search&query={itemname}&page={page_num}").json())
                items = []
                for auction in current_item_auctions:
                    try:
                        if auction["bin"] == True and auction["item_name"] == "Enchanted Book":
                            items.append(auction["starting_bid"])  # finds all book bins on ah
                    except KeyError:
                        pass
                items = sorted(items)
                if not items:
                    continue
                return items[0]  # only returns lowest bin
        else:
            for page_num in range(total_pages):
                current_item_auctions = list(requests.get(
                    f"https://hyskyapi.000webhostapp.com/apihandle.php?req=search&query={itemname}&page={page_num}").json())
                items = []
                for auction in current_item_auctions:
                    try:
                        if auction["bin"] == True:
                            items.append(auction["starting_bid"])
                    except KeyError:
                        pass
                items = sorted(items)
                if not items:
                    continue
                return items[0]  # see above lol


def get_recipe(itemname):
    recipe_ids = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
    current_item_recipe = []
    item_path = "./neu-repo/items/{}".format(itemname)
    print(item_path, itemname)
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


def get_craft_cost(itemname, nestings):
    item_file = itemname + ".json"
    recipe = get_recipe(item_file)
    craft_cost = []
    for item in recipe:
        item_file = item + ".json"
        if get_recipe(item_file) != "":
            head, sep, tail = recipe[item].partition(":")
            bazaarable = isBazaarable(head)
            auctionable = isAuctionable(head)
            if auctionable and bazaarable:
                ingredient_lowest_bin = get_lowest_bin(itemname, False)
                ingredient_lowest_bz_cost = total_bazaar_price(itemname)
                if ingredient_lowest_bz_cost > ingredient_lowest_bin:
                    craft_cost.append([item, ingredient_lowest_bin])
                    print(craft_cost)
                else:
                    craft_cost.append([item, ingredient_lowest_bz_cost])
                    print(craft_cost)
            elif bazaarable:
                ingredient_lowest_bz_cost = total_bazaar_price(itemname)
                craft_cost.append([item, ingredient_lowest_bz_cost])
                print(craft_cost)
            elif auctionable:
                ingredient_lowest_bin = get_lowest_bin(itemname, False)
                craft_cost.append([item, ingredient_lowest_bin])
                print(craft_cost)
        else:
            nestings += 1
            if nestings < 7:
                get_craft_cost(item, nestings)
            else:
                return craft_cost
    return craft_cost


def craft_flipper():
    items = list(os.listdir("./neu-repo/items"))
    potential_bazaar_tier_ups = []
    bazaar_tier_ups = []
    potential_flips = []
    flips = []
    isBook = False
    for item in items:
        item_path = "./neu-repo/items/{}".format(item)
        current_item = open(item_path, "r", encoding="utf-8")
        current_item = json.loads(current_item.read())
        current_item_name = current_item["internalname"]
        if "Enchanted Book" in current_item["displayname"]:
            isBook = True
        current_item_api_data = requests.get("https://api.hypixel.net/resources/skyblock/items")
        current_item_api_data = json.loads(current_item_api_data.text)
        for i in range(len(current_item_api_data["items"])):
            try:
                if current_item_api_data["items"][i]["id"] == current_item_name:
                    current_item_name_formatted = current_item_api_data["items"][i]["name"]
            except IndexError:
                break
        if isVanilla(current_item_name) == False:
            if "recipe" in current_item:
                current_item_recipe = current_item["recipe"]
                if isBazaarable(current_item_name) == True:
                    potential_bazaar_tier_ups.append(current_item_name)
                    profit = bazaar_tier_up(current_item_name)
                    if profit != "":
                        bazaar_tier_ups.append([current_item_name, profit])
                elif isAuctionable(current_item_name_formatted) == True:
                    print(current_item_name, "is auctionable")
                    potential_flips.append([current_item_name, get_lowest_bin(current_item_name_formatted, isBook)])
                    print(potential_flips)

    return bazaar_tier_ups, flips


# ----------------------------------------------------------------------------------------------------------------------
# main

# Repo.clone_from("https://github.com/Moulberry/NotEnoughUpdates-REPO.git", "./neu-repo/")
# craft_flipper()
print(get_craft_cost("TERMINATOR", nestcount))
