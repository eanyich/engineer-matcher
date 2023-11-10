import sqlite3
import pandas as pd
from io import StringIO

class Database:
    def __init__(self, engineers_csv, tickets_csv):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        
        # Load CSV data into SQLite memory database
        engineers_df = pd.read_csv(StringIO(engineers_csv))
        tickets_df = pd.read_csv(StringIO(tickets_csv))
        
        # Convert dataframes to SQL tables
        engineers_df.to_sql("engineers", self.conn, index=False, if_exists="replace")
        tickets_df.to_sql("tickets", self.conn, index=False, if_exists="replace")

    def get_all_tickets(self):
        return pd.read_sql_query("SELECT * FROM tickets", self.conn)

    def query_db(self, query):
        return pd.read_sql_query(query, self.conn)

    def get_engineers(self, ticket_id: int):
        query = """
        SELECT e.* FROM engineers e
        JOIN tickets t ON e.region like t.customer_country
        WHERE t.id = ? AND e.workload <= 3 AND e.status = 'Working'
        ORDER BY e.seniority DESC
        """
        query = """
        SELECT e.* FROM engineers e
        JOIN tickets t ON e.region like t.customer_country
        WHERE t.id = ?
        """
        return pd.read_sql_query(query, self.conn, params=(ticket_id,))

    def get_ticket_by_id(self, ticket_id: int):
        query = """
        SELECT * FROM tickets
        WHERE id = ?
        """
        self.cursor.execute(query, (ticket_id,))
        ticket = self.cursor.fetchone()

        return ticket

    def get_next_ticket_id(self) -> int:
        """
        Fetches the highest ticket_id from the tickets table and returns the next available ticket_id.
        """
        query = "SELECT MAX(id) FROM tickets"
        self.cursor.execute(query)
        max_id = self.cursor.fetchone()[0]
        
        # If there are no entries in the table, we start with ID 1, else we add 1 to the highest ID.
        if max_id is None:
            return 1
        else:
            return max_id + 1
