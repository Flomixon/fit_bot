from aiogram import types

from my_keyboard import start_kb


def merge_dict(li1: list, li2: list) -> dict[dict]:
    return {f'Подход {i+1}': {
        "Колличество повторений": li1[i],
        "Вес и доп. информация": li2[i]
        } for i in range(len(li1))
    }


async def main_menu(message: types.Message):
    await message.answer(
        'Выберите действие',
        reply_markup=start_kb())
