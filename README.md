# bannerlord-merchant-routes
![Autocomplete](https://img.shields.io/badge/Autocomplete-blue)
![Selectable](https://img.shields.io/badge/Selectable-green)
![Colorful CLI](https://img.shields.io/badge/Colorful_CLI-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791)
![Python](https://img.shields.io/badge/Python-336791)

A helping tool for the merchants of Mount &amp; Blade II: Bannerlord

## 🏃 Start
- Create the database following the provided graph. Consistent data are provided in public folder.
- Create a .env following the provided .env.example format
- Install dependency:
```
pip install -r requirements.txt
```
- Run:
```
python -m src.main
```

## 🚀 Features

1. **Record Market Trades**
   - Capture item trades with buy/sell towns, prices, auto-calculated profit, in-game date time

2. **Search & Filter Records**
   - View all records or filter by town/item sorted by profit and in-game date time

3. **Delete A Market Record**
   - Select record to delete

4. **Dynamic Data Entry**
   - Create new items and item types seamlessly during workflows

## 📚 Data Model

```mermaid
erDiagram

    ITEMTYPE {
        int itemtypeid PK
        text name
        timestamp createdts
        timestamp updatedts
    }

    ITEM {
        int itemid PK
        int itemtypeid FK
        text name
        timestamp createdts
        timestamp updatedts
    }

    MARKETRECORD {
        int marketrecordid PK
        int itemid FK
        int buytownid FK
        int selltownid FK
        int buyprice
        int sellprice
        int profit
        text season
        int day
        int year
        timestamp createdts
        timestamp updatedts
    }

    REGION {
        int regionid PK
        text name
        timestamp createdts
        timestamp updatedts
    }

    TOWN {
        int townid PK
        text name
        int regionid FK
        timestamp createdts
        timestamp updatedts
    }

    SEASON {
        text name PK
        timestamp createdts
        timestamp updatedts
    }

    %% Relationships

    ITEMTYPE ||--o{ ITEM : has

    ITEM ||--o{ MARKETRECORD : traded_in

    REGION ||--o{ TOWN : contains

    TOWN ||--o{ MARKETRECORD : buytown
    TOWN ||--o{ MARKETRECORD : selltown

    SEASON ||--o{ MARKETRECORD : time
```