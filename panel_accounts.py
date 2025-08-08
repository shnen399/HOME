def load_accounts():
    with open("自動發文主帳號.txt", "r") as f:
        lines = f.readlines()
    return [tuple(line.strip().split(":")) for line in lines]

def mark_failed_login(email):
    with open("自動發文主帳號.txt", "r") as f:
        lines = f.readlines()
    count = {}
    with open("自動發文主帳號.txt", "w") as f:
        for line in lines:
            user = line.strip().split(":")[0]
            count[user] = count.get(user, 0) + 1
            if count[user] < 3:
                f.write(line)
