'''This program finds products with the biggest difference between buy and sell offers and ranks them by most profit.
If I have time I will also include profit % and order filling speed.'''

import requests, HTML, json, os, re


while True:
    apiKey = "c9e849c0-6be0-4187-b209-e1f4674608b7"
    break
#api key - hidden for obvious reasons

def bazaar_flipper():
    bazaar_webpage = requests.get("https://api.slothpixel.me/api/skyblock/bazaar/")
    bazaar_data = json.loads(bazaar_webpage.text) #acquiring data from api
    bazaar_items = open("Items.json", "r")
    bazaar_items = json.loads(bazaar_items.read())

    products = list(requests.get("https://api.hypixel.net/skyblock/bazaar?key=" + apiKey).json()["products"].keys()) #collects products from api
    buy_order_price = []
    sell_order_price = []
    product_margins = []
    profit_percentage = []
    item_names = [] #initialising variables

    products.remove("ENCHANTED_CARROT_ON_A_STICK")
    products.remove("BAZAAR_COOKIE")
    bazaar_items.pop("ENCHANTED_CARROT_ON_A_STICK") #removes glitched products

    for i in range(len(products)):
        buy_order_price.append(bazaar_data[products[i]]["buy_summary"][0]["pricePerUnit"]) #finds lowest buy price
        sell_order_price.append(bazaar_data[products[i]]["sell_summary"][0]["pricePerUnit"]) #finds highest sell price
        product_margins.append(round((buy_order_price[i]-sell_order_price[i]), 1)) #calculates margin
        profit_percentage.append(round(product_margins[i]/buy_order_price[i], 2)) #calculates % profit
        profit_percentage[i] = "{:,}".format(profit_percentage[i])
        product_margins[i] = "{:,}".format(product_margins[i])
        item_names.append(bazaar_items[products[i]])


    final_products = zip(item_names, products, product_margins, profit_percentage) #combines the lists

    return final_products

def build_table():
    table_data = bazaar_flipper()
    HTMLFILE = './templates/flipper_data.html' #sets the file
    f = open(HTMLFILE, 'w+') #opens the file

    htmlcode = HTML.table(table_data, header_row=['Item', 'Id', 'Margin', 'Profit %']) #transforms it into a table with module magic

    f.write(htmlcode) #writes the table to the file

    t = open("./templates/flipper_data.html", "r+")
    replacement = t.read()
    replacement = replacement.replace('<TABLE border="1" style="border: 1px solid #000000; border-collapse: collapse;" cellpadding="4"', '<TABLE class="table table-striped" border="1" style="border: 1px solid #000000; border-collapse: collapse;" cellpadding="4" id="data"')
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
    items = list(os.listdir("./neu-repo/items"))
    vanilla_items = ["WOOD_AXE", "WOOD_HOE", "WOOD_PICKAXE","WOOD_SPADE", "WOOD_SWORD", "GOLD_AXE", "GOLD_HOE", "GOLD_PICKAXE", "GOLD_SPADE", "GOLD_SWORD", "ROOKIE_HOE"]
    for item in items:
        item_path = "./neu-repo/items/{}".format(item)
        current_item = open(item_path, "r", encoding="utf-8")
        current_item = json.loads(current_item.read())
        if pItem in vanilla_items:
            return True
        elif "vanilla" in current_item:
            return True
        else:
            return False

def craft_flipper():
    items = list(os.listdir("./neu-repo/items"))
    sb_items = []
    for item in items:
        item_path = "./neu-repo/items/{}".format(item)
        current_item = open(item_path, "r", encoding="utf-8")
        current_item = json.loads(current_item.read())
        current_item_name = current_item["internalname"]
        if "recipe" in current_item:
            current_item_recipe = current_item["recipe"]
            if isVanilla(current_item_name) == False:
                current_item_ah_name = re.sub(r"§4", '', current_item_name)
                current_item_ah_name = re.sub(r"§c", '', current_item_name)
                current_item_ah_name = re.sub(r"§6", '', current_item_name)
                current_item_ah_name = re.sub(r"§e", '', current_item_name)
                current_item_ah_name = re.sub(r"§2", '', current_item_name)
                current_item_ah_name = re.sub(r"§a", '', current_item_name)
                current_item_ah_name = re.sub(r"§b", '', current_item_name)
                current_item_ah_name = re.sub(r"§3", '', current_item_name)
                current_item_ah_name = re.sub(r"§1", '', current_item_name)
                current_item_ah_name = re.sub(r"§9", '', current_item_name)
                current_item_ah_name = re.sub(r"§d", '', current_item_name)
                current_item_ah_name = re.sub(r"§5", '', current_item_name)
                current_item_ah_name = re.sub(r"§f", '', current_item_name)
                current_item_ah_name = re.sub(r"§7", '', current_item_name)
                current_item_ah_name = re.sub(r"§8", '', current_item_name)
                current_item_ah_name = re.sub(r"§0", '', current_item_name)
                current_item_ah_name = re.sub(r"§k", '', current_item_name)
                current_item_ah_name = re.sub(r"§l", '', current_item_name)
                current_item_ah_name = re.sub(r"§m", '', current_item_name)
                current_item_ah_name = re.sub(r"§n", '', current_item_name)
                current_item_ah_name = re.sub(r"§o", '', current_item_name)
                current_item_ah_name = re.sub(r"§r", '', current_item_name)
                current_item_auctions = (requests.get("https://hyskyapi.000webhostapp.com/apihandle.php?req=search&query=" + current_item_ah_name).json()["auctions"])
                if current_item_auctions != "":
                    current_item_name.append(sb_items)

    print(sb_items)

craft_flipper()