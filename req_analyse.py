import requests
from config import *
from tgbot import bot
import asyncio

last_user_id = None
last_transaction_id = None
last_kyc_id = None
last_used_promocode_id = None
last_staking_id = None
last_request_id = None


async def get(call):
    req = requests.get(call)
    return req.json()


async def get_data(json_value, data_names):
    data_list = []
    for data_name in data_names:
        if not json_value[data_name]:
            data_list.append("-")
        else:
            data_list.append(json_value[data_name])
    return data_list


async def get_last_index(json_values, value_id):
    if value_id < 1:
        return -1
    for index in range(0, len(json_values)):
        if int(json_values[index]["id"]) == value_id:
            return index
    return await get_last_index(json_values, value_id - 1)  # if there is no value with this id, go back


async def get_changes(last_id, call, file_name, *value_data_names):
    json_values = await get(call)  # get all values
    with open(f"memory/{file_name}", "r+") as last_id_memory:
        last_id_content = last_id_memory.read()
        if not last_id:  # if last_id == None
            if last_id_content:
                last_id = int(last_id_content)
                start = await get_last_index(json_values, last_id)
            else:  # if last_id_content == ""
                start = -1
        else:
            start = await get_last_index(json_values, last_id)
        end = len(json_values)
        new_users_data = []  # list of new values
        if start < end - 1:
            for index in range(start + 1, end):
                last_id = int(json_values[index]["id"])
                new_users_data.append(await get_data(json_values[index], value_data_names))
            last_id_memory.seek(0)
            last_id_memory.write(str(last_id))
    if new_users_data:  # if the list is not empty
        return new_users_data
    return 0


async def get_value_data(value_id, call, data_name):
    json_values = await get(call)  # get all values
    for json_value in json_values:
        if json_value["id"] == value_id:
            return json_value[data_name]


async def set_last_id(file_name):
    with open(f"memory/{file_name}", "r") as last_id_memory:
        last_id = last_id_memory.read()
        return int(last_id)


async def get_value_data_by_index(index, call, data_name):
    json_values = await get(call)  # get all values
    return json_values[index][data_name]


async def send_message_to_admins(message):
    for ADMIN in ADMINS:
        await bot.send_message(ADMIN, message, parse_mode="HTML")


async def check_changes():
    while True:
        global last_user_id, last_transaction_id, last_kyc_id, last_used_promocode_id, last_staking_id, last_request_id
        await asyncio.sleep(10)

        # USERS
        all_new_users = await get_changes(last_user_id, ALL_USERS, "last_user_id.txt",
                                          "username", "email")
        if all_new_users:
            last_user_id = await set_last_id("last_user_id.txt")
            for new_user in all_new_users:
                username, email = new_user
                mess = (
                    f"🔔 <b>НОВИЙ ЮЗЕР</b> 🔔\n\n👤 <b>Пошта:</b> {email}\n👤 <b>Юзернейм:</b> "
                    f"{username}\n\n🛜 <em>Перегляньте подробиці в адмінпанелі за "
                    f"<a href=\"https://leaque.com/api/admin/user_app/user/\">посиланням</a></em>"
                )
                await send_message_to_admins(mess)

        # KYC
        all_new_kyc = await get_changes(last_kyc_id, ALL_KYS, "last_kyc_id.txt", "user", "first_name", "last_name",
                                        "address", "country", "birth_date", "mobile", "id_type", "id_number")
        if all_new_kyc:
            last_kyc_id = await set_last_id("last_kyc_id.txt")
            for new_kyc in all_new_kyc:
                user, first_name, last_name, address, country, birth_date, mobile, id_type, id_number = new_kyc
                email = await get_value_data(user, ALL_USERS, "email")
                mess = (
                    f"🔔 <b>НОВИЙ KYC</b> 🔔\n\n👤 <b>Юзер:</b> {email}\n👤 <b>Імʼя:</b> "
                    f"{first_name}\n👤 <b>Прізвище:</b> {last_name}\n👤 <b>Країна:</b> {country}\n"
                    f"👤 <b>Адреса:</b> {address}\n👤 <b>Дата Народження:</b> {birth_date}\n👤 "
                    f"<b>Телефон:</b> {mobile}\n👤 <b>Документ:</b> {id_type}\n👤 <b>Номер:</b> "
                    f"{id_number}\n\n🛜 <em>Будь ласка перевірте документи в адмінпанелі за "
                    f"<a href=\"https://leaque.com/api/admin/user_app/verificationrequest/\">"
                    f"посиланням</a></em>"
                )
                await send_message_to_admins(mess)

        # PROMOCODES
        all_new_promocodes = await get_changes(last_used_promocode_id, ALL_USED_PROMOCODES,
                                               "last_used_promocode_id.txt", "user", "promocode")
        if all_new_promocodes:
            last_used_promocode_id = await set_last_id("last_used_promocode_id.txt")
            for new_promocode in all_new_promocodes:
                user, promocode = new_promocode
                email = await get_value_data(user, ALL_USERS, "email")
                promocode_code = await get_value_data(promocode, ALL_PROMOCODES, "code")
                promocode_gift = await get_value_data(promocode, ALL_PROMOCODES, "gift")
                promocode_crypto = await get_value_data(promocode, ALL_PROMOCODES, "crypto")
                currency = await get_value_data_by_index(promocode_crypto, CRYPTO_CURRENCY, "index")
                mess = (
                    f"🔔 <b>ВИКОРИСТАННЯ ПРОМОКОДУ</b> 🔔\n\n👤 <b>Юзер:</b> {email}\n🎫 <b>Код:</b>"
                    f" {promocode_code}\n🎁 <b>Винагорода:</b> {promocode_gift} {currency}\n\n🛜 "
                    f"<em>Перегляньте подробиці в адмінпанелі за <a href="
                    f"\"https://leaque.com/api/admin/user_app/userbalance/\">посиланням</a></em>"
                )
                await send_message_to_admins(mess)

        # TRANSACTIONS
        all_new_transactions = await get_changes(last_transaction_id, ALL_TRANSACTIONS, "last_transaction_id.txt",
                                                 "user", "amount", "status", "time", "address", "transaction_id",
                                                 "balance", "transaction_type")
        if all_new_transactions:
            last_transaction_id = await set_last_id("last_transaction_id.txt")
            for new_transaction in all_new_transactions:
                user, amount, status, time_temp, address, transaction_id, balance, transaction_type = new_transaction
                email = await get_value_data(user, ALL_USERS, "email")
                time = time_temp[:8]

                # DEPOSIT
                if transaction_type == "Deposit":
                    mess = (
                        f"🔔 <b>НОВИЙ ДЕПОЗИТ</b> 🔔\n\n👤 <b>Юзер:</b> {email}\n💰 <b>Сума:</b>"
                        f" {amount}\n✅ <b>Статус:</b> {status}\n🕒 <b>Час:</b> "
                        f"{time}\n\n🛜 <em>Будь ласка перевірте ваш гаманець!</em>"
                    )
                    await send_message_to_admins(mess)

                # TRANSFER
                elif transaction_type == "Send":
                    if "success" in status.lower():
                        status = "Success"
                    mess = (
                        f"🔔 <b>НОВИЙ ТРАНСФЕР</b> 🔔\n\n🆔 {transaction_id}\n👤 <b>Відправник:</b> "
                        f"{email}\n👤 <b>Отримувач:</b> {address}\n💰 <b>Сума:</b> {amount}\n✅ "
                        f"<b>Статус:</b> {status}\n🕒 <b>Час:</b> {time}\n\n🛜 "
                        f"<em>Перегляньте подробиці в адмінпанелі за <a href="
                        f"\"https://leaque.com/api/admin/transactions/transaction/\">посиланням</a>"
                        f"</em>"
                    )
                    await send_message_to_admins(mess)

                # SWAP
                elif transaction_type == "Swap":
                    mess = (
                        f"🔔 <b>НОВИЙ СВАП</b> 🔔\n\n👤 <b>Юзер:</b> {email}\n💰 <b>Сума:</b>"
                        f" {amount}\n💰 <b>Отримав:</b> {balance}\n✅ <b>Статус:</b> {status}\n"
                        f"🕒 <b>Час:</b> {time}\n\n🛜 <em>Перегляньте подробиці в адмінпанелі за "
                        f"<a href=\"https://leaque.com/api/admin/transactions/transaction/\">"
                        f"посиланням</a></em>"
                    )
                    await send_message_to_admins(mess)

                # WITHDRAW
                elif transaction_type == "Withdraw":
                    mess = (
                        f"🔔 <b>НОВИЙ ЗАПИТ НА ВИВЕДЕННЯ КОШТІВ</b> 🔔\n\n👤 <b>Юзер:</b> {email}"
                        f"\n👤 <b>Гаманець:</b> {address}\n💰 <b>Сума:</b> {amount}\n✅ "
                        f"<b>Статус:</b> {status}\n🕒 <b>Час:</b> {time}\n\n🛜 <em>Перегляньте "
                        f"подробиці в адмінпанелі за "
                        f"<a href=\"https://leaque.com/api/admin/transactions/withdraw/\">"
                        f"посиланням</a></em>"
                    )
                    await send_message_to_admins(mess)

        # STAKING
        all_new_staking = await get_changes(last_staking_id, ALL_STAKING, "last_staking_id.txt", "user", "currency",
                                            "amount", "percentage", "date", "duration")
        if all_new_staking:
            last_staking_id = await set_last_id("last_staking_id.txt")
            for new_staking in all_new_staking:
                user, currency, amount, percentage, date, duration = new_staking
                email = await get_value_data(user, ALL_USERS, "email")
                staking_currency = await get_value_data_by_index(currency, CRYPTO_CURRENCY, "index")
                duration = duration.split(" ")[0]
                if duration[-1] == '1':
                    duration += " день"
                elif duration[-1] == '2' or duration[-1] == '3' or duration[-1] == '4':
                    duration += " дні"
                else:
                    duration += " днів"
                mess = (
                    f"🔔 <b>НОВИЙ СТЕЙКІНГ</b> 🔔\n\n👤 <b>Юзер:</b> {email}"
                    f"\n🔘 <b>Монета:</b> {staking_currency}\n💰 <b>Сума:</b> {amount}\n💰 <b>Процент:</b> "
                    f"{percentage}%\n🗓️ <b>Дата старта:</b> {date}\n🗓️ <b>Тривалість:</b> {duration}\n\n🛜 <em>"
                    f"Перегляньте подробиці в адмінпанелі за "
                    f"<a href=\"https://leaque.com/api/admin/transactions/staking/\">"
                    f"посиланням</a></em>"
                )
                await send_message_to_admins(mess)

        # SUPPORT REQUESTS
        all_new_requests = await get_changes(last_request_id, ALL_CHAT_REQUESTS, "last_request_id.txt", "email",
                                             "mobile", "telegram", "message")
        if all_new_requests:
            last_request_id = await set_last_id("last_request_id.txt")
            for new_request in all_new_requests:
                email, mobile, telegram, message = new_request
                mess = (
                    f"🔔 <b>НОВИЙ ЗАПИТ У SUPPORT</b> 🔔\n\n👤 <b>Пошта:</b> {email}\n👤 <b>Телефон:</b> "
                    f"{mobile}\n👤 <b>Телеграм:</b> {telegram}\n✉️ <b>Повідомлення:</b> {message}\n\n🛜 <em>"
                    f"Перегляньте подробиці в адмінпанелі за "
                    f"<a href=\"https://leaque.com/api/admin/chat/chatrequest/\">посиланням</a></em>"
                )
                await send_message_to_admins(mess)
