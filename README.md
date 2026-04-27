# Bannerlord Merchan Routes
![Autocomplete](https://img.shields.io/badge/Autocomplete-blue)
![Selectable](https://img.shields.io/badge/Selectable-green)
![Colorful CLI](https://img.shields.io/badge/Colorful_CLI-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791)

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
   - Capture item trades with buy/sell towns, prices, and notes (auto profit calculation)
   - *TODO: turn note into a true in-game date system*

2. **Search & Filter Records**
   - View all records or filter by town with buy/sell role context
   - *TODO: pagination in coming*

3. **Edit Market Records**
   - Update notes for existing entries with immediate feedback
   - *TODO: more edit options incoming*

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
        text note
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

    %% Relationships

    ITEMTYPE ||--o{ ITEM : "has"

    ITEM ||--o{ MARKETRECORD : "traded in"

    REGION ||--o{ TOWN : "contains"

    TOWN ||--o{ MARKETRECORD : "buytown"
    TOWN ||--o{ MARKETRECORD : "selltown"
```

## 🖼️ Sample Image

<img width="345" height="137" alt="image" src="https://github.com/user-attachments/assets/27ca6e24-9d36-4741-8743-d452a9cc0c16" />
<img width="297" height="141" alt="image" src="https://github.com/user-attachments/assets/c99354a5-e6db-451a-8714-f84205c339c7" />
<img width="980" height="351" alt="image" src="https://github.com/user-attachments/assets/34e58fd4-6be2-4ba7-95b5-a88988fb54fb" />
<img width="873" height="293" alt="image" src="https://github.com/user-attachments/assets/8f47773a-9f81-4c5b-8d70-e461a713233a" />


