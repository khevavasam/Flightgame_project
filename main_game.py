import mysql.connector

# Constants.
DB_CONFIG = {
    "user": "",
    "password": "",
    "host": "127.0.0.1",
    "port": 3306,
    "database": "flight_game",
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "autocommit": True,
}


# Functions.
def get_airport_by_name(name: str):
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    sql = "SELECT ident, name, iso_country, latitude_deg AS lat, longitude_deg AS lon FROM airport where name LIKE Concat('%', %s,'%')"
    cursor.execute(sql, (name,))
    row = cursor.fetchone()
    connection.close()
    if row:
        return row
    else:
        return f"Airport not found with name: {name}"


# Main program.
is_running = True

# Game loop.
while is_running:
    player_command = input("Enter name of an airport (exit to quit): ")
    if player_command.lower() == "exit":
        is_running = False
        continue
    airport_to_print = get_airport_by_name(player_command)
    print(airport_to_print)


print("Exiting game...")
