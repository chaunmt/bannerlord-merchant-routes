import os
import psycopg
import questionary
from rich import print
from tabulate import tabulate
from dotenv import load_dotenv

#===========================================================================================#
#---------------------------------------- DATABASE -----------------------------------------#
#===========================================================================================#
load_dotenv()
conn = psycopg.connect(
    dbname = os.getenv("DB_NAME"),
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASSWORD"),
    host = os.getenv("DB_HOST", "localhost"),
    port = int(os.getenv("DB_PORT", 5432))
)
conn.autocommit = True
cur = conn.cursor()

#===========================================================================================#
#------------------------------------ CREATION SERVICE -------------------------------------#
#===========================================================================================#
def create_itemtype():
    print("\n[purple3]Create new item's type[/purple3]\n")

    itemtypename = questionary.text("Enter new item type name:").ask()
    if not itemtypename:
        return None

    cur.execute("insert into itemtype(name) values (%s) returning itemtypeid",(itemtypename,))

    itemtypeid = cur.fetchone()[0]
    print(f"\nCreated item's type {itemtypename}\n")

    return itemtypeid

def create_item():
    print("\n[purple3]Create new item[/purple3]\n")

    itemname = questionary.text("Enter new item name:").ask()
    if not itemname:
        return None

    itemtypeid = select_or_create_entity(ITEMTYPE, allow_create=True)
    if not itemtypeid:
        return None

    cur.execute("insert into item(name, itemtypeid) values (%s, %s) returning itemid",(itemname, itemtypeid,))

    itemid = cur.fetchone()[0]
    print(f"\nCreated item {itemname}\n")

    return itemid

def create_entity(entity):
    if entity == ITEM:
        return create_item()
    elif entity == ITEMTYPE:
        return create_itemtype()
    else:
        return NotImplementedError

#===========================================================================================#
#----------------------------------- SUGGESTION SERVICE ------------------------------------#
#===========================================================================================#
ITEM = "item"
ITEMTYPE = "itemtype"
TOWN = "town"

def select_or_create_entity(entity_type, prompt=None, allow_create=False):
    query = f"select {entity_type}id as id, name from {entity_type} order by name"
    cur.execute(query)
    rows = cur.fetchall()

    name_to_id = {name: _id for _id, name in rows}

    selected = questionary.autocomplete(prompt or f"Search {entity_type}:",
                                        choices=list(name_to_id.keys())).ask()

    if selected in name_to_id:
        return name_to_id[selected]
    
    print(f"No valid {entity_type} selected.\n")

    if allow_create:
        choice = questionary.confirm(f"Create new {entity_type}?").ask()
        if choice:
            return create_entity(entity_type)
        
def select_marketrecord():
    headers, query, params = build_marketrecord_query(getid=True)
    cur.execute(query, params)
    rows = cur.fetchall()

    choices = []
    index_to_id = {}

    for idx, row in enumerate(rows, start=1):
        marketrecordid, item, buytown, selltown, buy, sell, profit, season, day, year = row

        label = f"[{idx}] {item} | {buytown} → {selltown} | Profit: {profit} | Date: {season} {day}, {year}"
        choices.append(label)
        index_to_id[label] = marketrecordid

    selected = questionary.select(
        "Select market record:",
        choices=choices
    ).ask()

    if not selected:
        return None

    return index_to_id[selected]

def select_season():
    query = f"select name from season"
    cur.execute(query)
    rows = cur.fetchall()

    seasons = [name for (name,) in rows]

    selected = questionary.autocomplete("Search season:", choices=seasons).ask()

    if selected in seasons:
        return selected

    print("No valid season selected.\n")

#===========================================================================================#
#-------------------------------------- QUERY SERVICE --------------------------------------#
#===========================================================================================#

def build_marketrecord_query(getid=False, townid=None, marketrecordid=None, itemid=None):
    headers = []
    conditions = []
    params = {}
    query = "select "
    if getid:
        query += "m.marketrecordid as id,"

    query = query + """
           i.name       as itemname,
           bt.name      as buytown,
           st.name      as selltown,
           m.buyprice   as cost,
           m.sellprice  as revenue,
           m.profit     as profit,
           m.season     as season,
           m.day        as day,
           m.year       as year
    from marketrecord m
        inner join item i on m.itemid = i.itemid
        inner join town bt on bt.townid = m.buytownid
        inner join town st on st.townid = m.selltownid
    """

    if townid:
        conditions.append("(m.buytownid = %(townid)s or m.selltownid = %(townid)s)")
        params["townid"] = townid
    if marketrecordid:
        conditions.append("(m.marketrecordid = %(marketrecordid)s)")
        params["marketrecordid"] = marketrecordid
    if itemid:
        conditions.append("(m.itemid = %(itemid)s)")
        params["itemid"] = itemid

    if conditions:
        query += "\nwhere " + "\nand ".join(conditions)

    query += """
    order by profit desc,
             year desc,
             case season
                when 'Spring' then 1
                when 'Summer' then 2
                when 'Autumn' then 3
                when 'Winter' then 4
             end desc,
             day desc,
             itemname desc;
    """

    if getid:
        headers.append("ID")
    headers.extend(["Item", "Buy Town", "Sell Town", "Cost", "Revenue", "Profit", "Season", "Day", "Year"])

    return headers, query, params

def get_and_print_table(headers, query, params):
    cur.execute(query, params)
    rows = cur.fetchall()
    print(tabulate(
        headers=headers,
        tabular_data=rows,
        tablefmt="psql"
    ))
    return rows

#===========================================================================================#
#------------------------------ FEATURE 1: RECORD MARKET INFO ------------------------------#
#===========================================================================================#
def write_marketrecord():
    while True:
        try:
            print("\n[green]=== Record Market Info ===[/green]")
            print("[dim](Ctrl+C = cancel or back to menu)[/dim]\n")

            confirm = False

            itemid = select_or_create_entity(ITEM, allow_create=True)
            if not itemid:
                raise KeyboardInterrupt
            
            buytownid = select_or_create_entity(TOWN, prompt="Search town buy from:")
            if not buytownid:
                raise KeyboardInterrupt
            
            selltownid = select_or_create_entity(TOWN, prompt="Search town sell at:")
            if not selltownid:
                raise KeyboardInterrupt
            
            buyprice = questionary.text("Buy price:").ask()
            if not buyprice:
                raise KeyboardInterrupt
            
            sellprice = questionary.text("Sell price:").ask()
            if not sellprice:
                raise KeyboardInterrupt

            season = select_season()
            if not season:
                raise KeyboardInterrupt
            
            day = questionary.text("Day:").ask()
            if not day:
                raise KeyboardInterrupt
            
            year = questionary.text("Year:").ask()
            if not year:
                raise KeyboardInterrupt

            # Confirm
            confirm = questionary.confirm("Save record?").ask()
            if confirm:

                # Insert
                cur.execute("""
                    insert into marketrecord (itemid, buytownid, selltownid, buyprice, sellprice, season, day, year)
                    values (%s, %s, %s, %s, %s, %s, %s, %s)
                    returning marketrecordid
                """, (itemid, buytownid, selltownid, int(buyprice), int(sellprice), season, int(day), int(year)))            

                # Print out record just save
                marketrecordid = cur.fetchone()[0]
                if marketrecordid:
                    print("\nMarket record saved!\n")
                    find_marketrecords_by_id(marketrecordid)
                else:
                    print("\nUnable to save market record\n")

            else:
                print("\nOk, try again\n")

        except KeyboardInterrupt:
            print("\n...Returning to main menu...\n")
            break

#===========================================================================================#
#----------------------------- FEATURE 2: FIND MARKET RECORDS ------------------------------#
#===========================================================================================#
def find_all_marketrecords():
    headers, query, params = build_marketrecord_query()
    return get_and_print_table(headers, query, params)

def find_marketrecords_by_town():
    townid = select_or_create_entity(TOWN)
    if townid:
        headers, query, params = build_marketrecord_query(townid=townid)
        return get_and_print_table(headers, query, params)
    
def find_marketrecords_by_item():
    itemid = select_or_create_entity(ITEM)
    if itemid:
        headers, query, params = build_marketrecord_query(itemid=itemid)
        return get_and_print_table(headers, query, params)

def find_marketrecords_by_id(marketrecordid):
    headers, query, params = build_marketrecord_query(marketrecordid=marketrecordid)
    rows = get_and_print_table(headers, query, params)
    return rows[0] if rows else None

def find_marketrecords():
    while True:
        try:
            print("\n[green]=== Find Market Records ===[/green]")
            print("[dim](Ctrl+C = cancel or back to menu)[/dim]\n")

            choice = questionary.select("Filter market records by:",
                                        choices=["1. All records",
                                                 "2. By town",
                                                 "3. By item"]).ask()
            if not choice:
                raise KeyboardInterrupt
            
            if choice.startswith("1"):
                find_all_marketrecords()

            elif choice.startswith("2"):
                find_marketrecords_by_town()

            elif choice.startswith("3"):
                find_marketrecords_by_item()

        except KeyboardInterrupt:
            print("\n...Returning to main menu...\n")
            break

#===========================================================================================#
#----------------------------- FEATURE 3: DELETE A MARKET RECORD -----------------------------#
#===========================================================================================#
def delete_marketrecord():
    while True:
        try:
            print("\n[green]=== Edit Market Record ===[/green]\n")
            print("[dim](Ctrl+C = cancel or back to menu)[/dim]\n")

            marketrecordid = select_marketrecord()
            if not marketrecordid:
                print("No market record selected")
                return

            record = find_marketrecords_by_id(marketrecordid)
            if not record:
                print("Record not found")
                return

            # Confirm
            confirm = questionary.confirm("[red]Delete record?[/red]").ask()
            if confirm:
                # Delete
                cur.execute("delete from marketrecord where marketrecordid = %s", (marketrecordid,))
                print("\nMarket record deleted!\n")
            else:
                print("\nOk, try again\n")

        except KeyboardInterrupt:
            print("\n...Returning to main menu...\n")
            break

#===========================================================================================#
#---------------------------------------- MAIN MENU ----------------------------------------#
#===========================================================================================#
def main():
    while True:
        try:
            print("\n[green]=== Bannerlord Merchant Routes ===[/green]")
            print("[dim](Ctrl+C = exit)[/dim]\n")

            choice = questionary.select("What do you want to do?", 
                                        choices=["1. Record market information",
                                                 "2. Find market records",
                                                 "3. Delete a market record"]).ask()

            if not choice:
                raise KeyboardInterrupt
            
            if choice.startswith("1"):
                write_marketrecord()

            elif choice.startswith("2"):
                find_marketrecords()

            elif choice.startswith("3"):
                delete_marketrecord()

            else:
                print("Invalid selection")

        except KeyboardInterrupt:
            print("\n...Goodbye, see you again\n")
            break

if __name__ == "__main__":
    main()