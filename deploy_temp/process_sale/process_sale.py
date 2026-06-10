import azure.functions as func
import pymssql
import json
import os
import logging

def main(msg: func.ServiceBusMessage):
    sale_event = json.loads(msg.get_body().decode("utf-8"))
    product_id  = sale_event.get("product_id")
    quantity    = sale_event.get("quantity", 1)
    sale_id     = sale_event.get("sale_id", "unknown")
    logging.info(f"Processing sale {sale_id}: {quantity}x product {product_id}")
    server   = os.environ["SQL_SERVER"]
    database = os.environ["SQL_DATABASE"]
    username = os.environ["SQL_USERNAME"]
    password = os.environ["SQL_PASSWORD"]
    conn   = pymssql.connect(server, username, password, database)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Products SET CurrentStock = CurrentStock - %s, LastSaleDate = GETUTCDATE() WHERE ProductId = %s", (quantity, product_id))
        cursor.execute("INSERT INTO StockMovements (ProductId, MovementType, Quantity, Reference, MovedAt) VALUES (%s, 'SALE', %s, %s, GETUTCDATE())", (product_id, quantity, sale_id))
        cursor.execute("SELECT ProductName, CurrentStock, MinimumStock FROM Products WHERE ProductId = %s", (product_id,))
        row = cursor.fetchone()
        if row:
            product_name, current_stock, min_stock = row
            if current_stock <= min_stock:
                logging.warning(f"LOW STOCK: {product_name} | Current: {current_stock} | Minimum: {min_stock}")
        conn.commit()
        logging.info(f"Stock updated for product {product_id}. Sale {sale_id} processed.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Failed to process sale {sale_id}: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
