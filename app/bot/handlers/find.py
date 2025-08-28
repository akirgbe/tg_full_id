from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from db.database_new import new_db_instance as accounts_db

router = Router()


@router.message(Command("find_phone"))
async def find_phone_command(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Укажите номер телефона после /find_phone, например: /find_phone +1234567890")
        return

    phone_number = args[1]
    result = accounts_db.find_by_phone_number(phone_number)

    if not result["accounts"]:
        await message.answer(f"По номеру <code>{phone_number}</code> ничего не найдено", parse_mode="HTML")
        return

    response = f"Найдено по номеру <code>{phone_number}</code>:\n"
    response += f"<b>Аккаунты ({len(result['accounts'])}):</b>\n"
    for acc in result["accounts"]:
        response += f"- {acc['messenger_type'].capitalize()}: "
        if acc["telegram_id"]:
            response += f"Telegram ID=<code>{acc['telegram_id']}</ affirme>, Tag=<code>{acc['telegram_tag'] or 'нет'}</code>, "
        if acc["phone_number"]:
            response += f"Phone=<code>{acc['phone_number']}</code>, "
        if acc["whatsapp_id"]:
            response += f"WhatsApp ID=<code>{acc['whatsapp_id']}</code>, "
        if acc["email"]:
            response += f"Email=<code>{acc['email']}</code>"
        response += "\n"

    response += f"\n<b>Люди ({len(result['persons'])}):</b>\n"
    for person in result["persons"]:
        response += f"- {person['last_name']} {person['first_name']}"
        if person["middle_name"]:
            response += f" {person['middle_name']}"
        if person["description"]:
            response += f" ({person['description']})"
        response += f" (ID: <code>{person['id']}</code>)\n"

    await message.answer(response, parse_mode="HTML")


@router.message(Command("list_persons"))
async def list_persons_command(message: Message):
    persons = accounts_db.get_all_persons()
    if not persons:
        await message.answer("Список людей пуст")
        return

    response = "<b>Список людей:</b>\n"
    for person in persons:
        response += f"- {person.last_name} {person.first_name}"
        if person.middle_name:
            response += f" {person.middle_name}"
        if person.description:
            response += f" ({person.description})"
        response += f" (ID: <code>{person.id}</code>)\n"

    await message.answer(response, parse_mode="HTML")


@router.message(Command("list_accounts"))
async def list_accounts_command(message: Message):
    accounts = accounts_db.get_all_accounts()
    if not accounts:
        await message.answer("Список аккаунтов пуст")
        return

    response = "<b>Список аккаунтов:</b>\n"
    for acc in accounts:
        response += f"- {acc.messenger_type.capitalize()} (Person ID: <code>{acc.person_id}</code>): "
        if acc.telegram_id:
            response += f"Telegram ID=<code>{acc.telegram_id}</code>, Tag=<code>{acc.telegram_tag or 'нет'}</code>, "
        if acc.phone_number:
            response += f"Phone=<code>{acc.phone_number}</code>, "
        if acc.whatsapp_id:
            response += f"WhatsApp ID=<code>{acc.whatsapp_id}</code>, "
        if acc.email:
            response += f"Email=<code>{acc.email}</code>"
        response += "\n"

    await message.answer(response, parse_mode="HTML")


@router.message(Command("add_person"))
async def add_person_command(message: Message):
    args = message.text.split(maxsplit=3)
    if len(args) < 3:
        await message.answer(
            "Укажите фамилию и имя после /add_person, например: /add_person Иванов Иван [Иванович] [описание]")
        return

    last_name, first_name = args[1], args[2]
    middle_name = args[3] if len(args) > 3 else None
    description = args[4] if len(args) > 4 else None

    person_id = accounts_db.add_person(last_name, first_name, middle_name, description)
    if person_id:
        await message.answer(f"Человек добавлен с ID <code>{person_id}</code>", parse_mode="HTML")
    else:
        await message.answer("Ошибка при добавлении человека", parse_mode="HTML")


@router.message(Command("add_account"))
async def add_account_command(message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer(
            "Укажите person_id и тип мессенджера после /add_account, например: /add_account 1 telegram phone=+1234567890 id=123456789 tag=@ivanov")
        return

    try:
        person_id = int(args[1])
        params = args[2].split()
        messenger_type = params[0]
        kwargs = {}
        for param in params[1:]:
            key, value = param.split("=", 1)
            kwargs[key] = value

        if accounts_db.add_account(
                person_id=person_id,
                messenger_type=messenger_type,
                telegram_id=int(kwargs.get("id")) if kwargs.get("id") else None,
                telegram_tag=kwargs.get("tag"),
                phone_number=kwargs.get("phone"),
                whatsapp_id=kwargs.get("whatsapp_id"),
                email=kwargs.get("email")
        ):
            await message.answer(f"Аккаунт {messenger_type} добавлен для person_id=<code>{person_id}</code>",
                                 parse_mode="HTML")
        else:
            await message.answer(f"Ошибка: человек с ID <code>{person_id}</code> не найден или другая ошибка",
                                 parse_mode="HTML")
    except ValueError:
        await message.answer("Person ID должен быть числом")
    except Exception as e:
        await message.answer(f"Ошибка при добавлении аккаунта: {str(e)}", parse_mode="HTML")


@router.message(Command("delete_person"))
async def delete_person_command(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Укажите ID человека после /delete_person, например: /delete_person 1")
        return

    try:
        person_id = int(args[1])
        if accounts_db.delete_person(person_id):
            await message.answer(f"Человек с ID <code>{person_id}</code> и связанные аккаунты удалены",
                                 parse_mode="HTML")
        else:
            await message.answer(f"Человек с ID <code>{person_id}</code> не найден", parse_mode="HTML")
    except ValueError:
        await message.answer("ID человека должен быть числом")


@router.message(Command("delete_account"))
async def delete_account_command(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Укажите ID аккаунта после /delete_account, например: /delete_account 1")
        return

    try:
        account_id = int(args[1])
        if accounts_db.delete_account(account_id):
            await message.answer(f"Аккаунт с ID <code>{account_id}</code> удален", parse_mode="HTML")
        else:
            await message.answer(f"Аккаунт с ID <code>{account_id}</code> не найден", parse_mode="HTML")
    except ValueError:
        await message.answer("ID аккаунта должен быть числом")
