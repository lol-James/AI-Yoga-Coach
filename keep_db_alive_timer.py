from PyQt5.QtCore import QTimer

def start_keep_db_alive_timer(db_connection):
    """
    Starts a timer that sends a simple query to the database every 5 minutes
    to keep the connection alive.
    """
    def keep_db_alive():
        try:
            with db_connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_connection.commit()
            print("Database connection kept alive.")
        except Exception as e:
            print(f"Error keeping database connection alive: {e}")

    timer = QTimer()
    timer.timeout.connect(keep_db_alive)
    timer.start(5 * 60 * 1000)  # 5 minutes in milliseconds
    return timer