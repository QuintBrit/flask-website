'''This program finds products with the biggest difference between buy and sell offers and ranks them by most profit.
If I have time I will also include profit % and order filling speed.'''

import requests, HTML, json, os, re
from git import Repo
from dotenv import load_dotenv
load_dotenv()

apiKey = os.environ.get("apikey")


def bazaar_flipper():
    bazaar_webpage = requests.get("https://api.slothpixel.me/api/skyblock/bazaar/")
    bazaar_data = json.loads(bazaar_webpage.text)  # acquiring data from api
    bazaar_items = requests.get("https://api.hypixel.net/resources/skyblock/items")
    bazaar_items = json.loads(bazaar_items.text)

    products = list(requests.get("https://api.hypixel.net/skyblock/bazaar?key=" + apiKey).json()[
                        "products"].keys())  # collects products from api
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
                bazaar_items["items"].pop(i) # removes glitched products
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

    final_products = zip(item_names, products, product_margins, profit_percentage)  # combines the lists
    final_products_list = list(final_products)
    return final_products_list


def build_table():
    table_data = bazaar_flipper()
    HTMLFILE = './templates/flipper_data.html'  # sets the file
    f = open(HTMLFILE, 'w+')  # opens the file

    htmlcode = HTML.table(table_data, header_row=['Item', 'Id', 'Margin',
                                                  'Profit %'])  # transforms it into a table with module magic

    f.write(htmlcode)  # writes the table to the file

    t = open("./templates/flipper_data.html", "r+")
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
    t = open("./templates/flipper_data.html", "w+")
    t.write(replacement)


def isVanilla(pItem):
    vanilla_items = ["WOOD_AXE", "WOOD_HOE", "WOOD_PICKAXE", "WOOD_SPADE", "WOOD_SWORD", "GOLD_AXE", "GOLD_HOE",
                     "GOLD_PICKAXE", "GOLD_SPADE", "GOLD_SWORD", "ROOKIE_HOE"]
    filename = pItem + ".json"
    for root, dir, files in os.walk(".\\neu-repo\\items"):
        if filename in files:
            current_item = open(".\\neu-repo\\items\\"+filename, "r", encoding="utf-8", )
            current_item = json.loads(current_item.read())
            if pItem in vanilla_items:
                return True
            elif 'vanilla' in current_item:
                return True
            else:
                return False


def render_item(itemname):
    head = "https://sky.shiiyu.moe/item/".format(itemname)
    return head


def auction_declarations(itemname):
    formatting_codes = ["§4", "§c", "§6", "§e", "§2", "§a", "§b", "§3", "§1", "§9", "§d", "§5", "§f", "§7", "§8", "§0",
                        "§k", "§l", "§m", "§n", "§o", "§r"]
    for i in range(len(formatting_codes)):
        itemname = itemname.replace("{}".format(formatting_codes[i]), "")
    itemname = itemname.lower()
    itemname = re.sub(r" ", '', itemname)
    current_item_auctions = list(requests.get(
        "https://hyskyapi.000webhostapp.com/apihandle.php?req=search&query=" + itemname).json())

    return current_item_auctions


def isAuctionable(itemname):
    if auction_declarations(itemname) != []:
        return True


def isBazaarable(itemname):
    products = list(requests.get("https://api.hypixel.net/skyblock/bazaar?key=" + apiKey).json()[
                        "products"].keys())  # collects products from api
    if itemname in products:
        return True


def getLowestBin(itemname, isBook):
    total_pages = 100  #test value, we'll see how it goes
    while True:
        if isBook == True:
            itemname = "/ebs%20" + itemname
            for page_num in range(total_pages):
                current_item_auctions = list(requests.get(
                    f"https://hyskyapi.000webhostapp.com/apihandle.php?req=search&query={itemname}&page={page_num}").json())
                items = []
                for auction in current_item_auctions:
                    try:
                        if auction["bin"] == True and auction["item_name"] == "Enchanted Book":
                            items.append(auction["starting_bid"])
                    except KeyError:
                        pass
                items = sorted(items)
                if not items:
                    continue
                return items[0]


def craft_flipper():
    items = list(os.listdir("./neu-repo/items"))
    potential_bazaar_tier_ups = []
    potential_flips = []
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
                if isAuctionable(current_item_name_formatted) == True:
                    print(current_item_name, "is auctionable")
                    potential_flips.append([current_item_name, getLowestBin(current_item_name_formatted, isBook)])
                    print(potential_flips)
                elif isBazaarable(current_item_name) == True:
                    potential_bazaar_tier_ups.append(current_item_name)
                    print(current_item_name, "is bazaarable")




#Repo.clone_from("https://github.com/Moulberry/NotEnoughUpdates-REPO.git", "./neu-repo/")
craft_flipper()