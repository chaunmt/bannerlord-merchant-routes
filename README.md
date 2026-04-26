# bannerlord-merchant-routes
![Autocomplete](https://img.shields.io/badge/Autocomplete-blue)
![Selectable](https://img.shields.io/badge/Selectable-green)
![Colorful CLI](https://img.shields.io/badge/Colorful_CLI-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791)

A helping tool for the merchants of Mount &amp; Blade II: Bannerlord

## Data Model

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
        timestamptz createdts
        timestamptz updatedts
    }

    %% Relationships

    ITEMTYPE ||--o{ ITEM : "has"

    ITEM ||--o{ MARKETRECORD : "traded in"

    REGION ||--o{ TOWN : "contains"

    TOWN ||--o{ MARKETRECORD : "buytown"
    TOWN ||--o{ MARKETRECORD : "selltown"
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