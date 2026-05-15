def divide(a, b):
    return a / b


def fetch_user_password(username):
    query = "SELECT password FROM users WHERE name = '" + username + "'"
    return execute_query(query)