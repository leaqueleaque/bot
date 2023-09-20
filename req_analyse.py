import requests
from config import *
from tgbot import bot
import asyncio

last_user_id = -1
last_transaction_id = -1
last_kyc_id = -1
last_used_promocode_id = -1
last_staking_id = -1
last_request_id = -1


async def get(call):
    try:
        req = requests.get(call).json()
        return req
    except Exception as exc:
        print(f"ERROR! Невозможно получить данные по ссылке {call}")
        print(exc)
        return None


async def get_data(json_value, data_names):
    data_list = []
    for data_name in data_names:
        try:
            if json_value[data_name]:
                data_list.append(json_value[data_name])
            else:
                data_list.append("-")
        except Exception as exc:
            print(f"ERROR! В {json_value} нет данных с названием {data_name}")
            print(exc)
            data_list.append("'no data'")
    return data_list


async def get_changes(last_id, call, *value_data_names):
    json_values = await get(call)  # Получить все значения
    if json_values:
        new_values_data = []  # Список изменений
        max_id = last_id
        for value in json_values:
            if value["id"] > last_id:
                if max_id < value["id"]:
                    max_id = value["id"]
                new_values_data.append(await get_data(value, value_data_names))
        if new_values_data:  # Если есть изменения
            return new_values_data, max_id
    return 0


async def get_value_data(value_id, call, data_name):
    json_values = await get(call)  # get all values
    if json_values:
        for json_value in json_values:
            if json_value["id"] == value_id:
                return json_value[data_name]
    return None


async def get_value_data_by_index(index, call, data_name):
    try:
        json_values = await get(call)  # get all values
        value_data = json_values[index][data_name]
        return value_data
    except Exception as exc:
        print(f"ERROR! Невозможно получить данные по индексу {index} по ссылке {call}")
        print(exc)
        return None


async def send_message_to_admins(message):
    for ADMIN in ADMINS:
        try:
            await bot.send_message(ADMIN, message, parse_mode="HTML")
        except Exception as e:
            print(e)
            print(f"Удаление пользователя с id {ADMIN}")
            ADMINS.remove(ADMIN)


async def check_changes():
    while True:
        global last_user_id, last_transaction_id, last_kyc_id, last_used_promocode_id, last_staking_id, last_request_id
        await asyncio.sleep(20)

        # USERS
        all_new_users_c = await get_changes(last_user_id, ALL_USERS, "username", "email")

        if all_new_users_c:
            all_new_users, last_user_id = all_new_users_c
            for new_user in all_new_users:
                username, email = new_user
                mess = (
                    f"🔔 <b>НОВИЙ ЮЗЕР</b> 🔔\n\n👤 <b>Пошта:</b> {email}\n👤 <b>Юзернейм:</b> "
                    f"{username}\n\n🛜 <em>Перегляньте подробиці в адмінпанелі за "
                    f"<a href=\"https://cointranche.com/api/admin/user_app/user/\">посиланням</a></em>"
                )
                await send_message_to_admins(mess)

        # KYC
        all_new_kyc_c = await get_changes(last_kyc_id, ALL_KYS, "user", "first_name", "last_name",
                                        "address", "country", "birth_date", "mobile", "id_type", "id_number")

        if all_new_kyc_c:
            all_new_kyc, last_kyc_id = all_new_kyc_c
            for new_kyc in all_new_kyc:
                user, first_name, last_name, address, country, birth_date, mobile, id_type, id_number = new_kyc
                email = await get_value_data(user, ALL_USERS, "email")
                mess = (
                    f"🔔 <b>НОВИЙ KYC</b> 🔔\n\n👤 <b>Юзер:</b> {email}\n👤 <b>Імʼя:</b> "
                    f"{first_name}\n👤 <b>Прізвище:</b> {last_name}\n👤 <b>Країна:</b> {country}\n"
                    f"👤 <b>Адреса:</b> {address}\n👤 <b>Дата Народження:</b> {birth_date}\n👤 "
                    f"<b>Телефон:</b> {mobile}\n👤 <b>Документ:</b> {id_type}\n👤 <b>Номер:</b> "
                    f"{id_number}\n\n🛜 <em>Будь ласка перевірте документи в адмінпанелі за "
                    f"<a href=\"https://cointranche.com/api/admin/user_app/verificationrequest/\">"
                    f"посиланням</a></em>"
                )
                await send_message_to_admins(mess)

        # PROMOCODES
        all_new_used_promocodes_c = await get_changes(last_used_promocode_id, ALL_USED_PROMOCODES,
                                               "user", "promocode")

        if all_new_used_promocodes_c:
            all_new_used_promocodes, last_used_promocode_id = all_new_used_promocodes_c
            for new_promocode in all_new_used_promocodes:
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
                    f"\"https://cointranche.com/api/admin/user_app/userbalance/\">посиланням</a></em>"
                )
                await send_message_to_admins(mess)

        # TRANSACTIONS
        all_new_transactions_c = await get_changes(last_transaction_id, ALL_TRANSACTIONS,
                                                 "user", "amount", "status", "time_of_transaction", "address", "date",
                                                 "transaction_id", "balance", "transaction_type")

        if all_new_transactions_c:
            all_new_transactions, last_transaction_id = all_new_transactions_c
            for new_transaction in all_new_transactions:
                user, amount, status, time, address, date, transaction_id, balance, transaction_type = new_transaction
                email = await get_value_data(user, ALL_USERS, "email")

                # DEPOSIT
                if transaction_type == "Deposit":
                    mess = (
                        f"🔔 <b>НОВИЙ ДЕПОЗИТ</b> 🔔\n\n👤 <b>Юзер:</b> {email}\n💰 <b>Сума:</b>"
                        f" {amount}\n✅ <b>Статус:</b> {status}\n🕒 <b>Час:</b> "
                        f"{time} {date}\n\n🛜 <em>Будь ласка перевірте ваш гаманець!</em>"
                    )
                    await send_message_to_admins(mess)

                # TRANSFER
                elif transaction_type == "Send":
                    if "success" in status.lower():
                        status = "Success"
                    mess = (
                        f"🔔 <b>НОВИЙ ТРАНСФЕР</b> 🔔\n\n🆔 {transaction_id}\n👤 <b>Відправник:</b> "
                        f"{email}\n👤 <b>Отримувач:</b> {address}\n💰 <b>Сума:</b> {amount}\n✅ "
                        f"<b>Статус:</b> {status}\n🕒 <b>Час:</b> {time} {date}\n\n🛜 "
                        f"<em>Перегляньте подробиці в адмінпанелі за <a href="
                        f"\"https://cointranche.com/api/admin/transactions/transaction/\">посиланням</a>"
                        f"</em>"
                    )
                    await send_message_to_admins(mess)

                # SWAP
                elif transaction_type == "Swap":
                    mess = (
                        f"🔔 <b>НОВИЙ СВАП</b> 🔔\n\n👤 <b>Юзер:</b> {email}\n💰 <b>Сума:</b>"
                        f" {amount}\n💰 <b>Отримав:</b> {balance}\n✅ <b>Статус:</b> {status}\n"
                        f"🕒 <b>Час:</b> {time} {date}\n\n🛜 <em>Перегляньте подробиці в адмінпанелі за "
                        f"<a href=\"https://cointranche.com/api/admin/transactions/transaction/\">"
                        f"посиланням</a></em>"
                    )
                    await send_message_to_admins(mess)

                # WITHDRAW
                elif transaction_type == "Withdraw":
                    mess = (
                        f"🔔 <b>НОВИЙ ЗАПИТ НА ВИВЕДЕННЯ КОШТІВ</b> 🔔\n\n👤 <b>Юзер:</b> {email}"
                        f"\n👤 <b>Гаманець:</b> {address}\n💰 <b>Сума:</b> {amount}\n✅ "
                        f"<b>Статус:</b> {status}\n🕒 <b>Час:</b> {time} {date}\n\n🛜 <em>Перегляньте "
                        f"подробиці в адмінпанелі за "
                        f"<a href=\"https://cointranche.com/api/admin/transactions/withdraw/\">"
                        f"посиланням</a></em>"
                    )
                    await send_message_to_admins(mess)

        # STAKING
        all_new_staking_c = await get_changes(last_staking_id, ALL_STAKING, "user", "currency",
                                              "amount", "percentage", "date_start", "date_expiration")

        if all_new_staking_c:
            all_new_staking, last_staking_id = all_new_staking_c
            for new_staking in all_new_staking:
                user, currency, amount, percentage, date_start, date_expiration = new_staking
                email = await get_value_data(user, ALL_USERS, "email")
                currency_index = currency["index"]
                mess = (
                    f"🔔 <b>НОВИЙ СТЕЙКІНГ</b> 🔔\n\n👤 <b>Юзер:</b> {email}"
                    f"\n🔘 <b>Монета:</b> {currency_index}\n💰 <b>Сума:</b> {amount}\n💰 <b>Процент:</b> "
                    f"{percentage}%\n🗓️ <b>Дата старта:</b> {date_start}\n🗓️ <b>Дата завершення:</b> {date_expiration}"
                    f"\n\n🛜 <em>Перегляньте подробиці в адмінпанелі за "
                    f"<a href=\"https://cointranche.com/api/admin/transactions/staking/\">"
                    f"посиланням</a></em>"
                )
                await send_message_to_admins(mess)

        # SUPPORT REQUESTS
        all_new_requests_c = await get_changes(last_request_id, ALL_CHAT_REQUESTS, "email",
                                             "mobile", "telegram", "message")

        if all_new_requests_c:
            all_new_requests, last_request_id = all_new_requests_c
            for new_request in all_new_requests:
                email, mobile, telegram, message = new_request
                if "+" in mobile:
                    mobile_temp = mobile[2:]
                else:
                    mobile_temp = mobile
                if not mobile_temp.isdigit():
                    mobile = "-"
                mess = (
                    f"🔔 <b>НОВИЙ ЗАПИТ У SUPPORT</b> 🔔\n\n👤 <b>Пошта:</b> {email}\n👤 <b>Телефон:</b> "
                    f"{mobile}\n👤 <b>Телеграм:</b> {telegram}\n✉️ <b>Повідомлення:</b> {message}\n\n🛜 <em>"
                    f"Перегляньте подробиці в адмінпанелі за "
                    f"<a href=\"https://cointranche.com/api/admin/chat/chatrequest/\">посиланням</a></em>"
                )
                await send_message_to_admins(mess)