from datetime import datetime

from aiogram import types
from aiogram.filters.callback_data import CallbackData

from beanie import PydanticObjectId

from db import coll_exc, coll_train


class ExcercisesCallback(CallbackData, prefix="my_excercises"):
    obj: PydanticObjectId
    exc_name: str


class ExcersisesInfoCallback(ExcercisesCallback, prefix="change_info"):
    pass


class ExcersisesSetsCallback(ExcercisesCallback, prefix="input_set"):
    pass


class MuscleGroupCallback(CallbackData, prefix="muscle_group"):
    obj: PydanticObjectId


class ExcercisesAddCallback(CallbackData, prefix="add_excercises"):
    obj: PydanticObjectId


class TrainingCallback(CallbackData, prefix="training"):
    obj: PydanticObjectId


class ExcHistoryCallback(ExcercisesCallback, prefix="history_exc"):
    pass


def start_kb() -> types.InlineKeyboardMarkup:
    button = [[types.InlineKeyboardButton(
        text='Начать тренировку',
        callback_data="TrainStart"),
        types.InlineKeyboardButton(
            text='История тренировок',
            callback_data="TrainHistory"
        )]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=button)
    return keyboard


def cancel_kb() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(
            text='Отмена добавления',
            callback_data="CancelAddExcercises"
        )]]
    )
    return keyboard


def cancel_ex_kb() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(
            text='Завершить упражнение',
            callback_data="CancelExcercises"
        )]]
    )
    return keyboard


async def excercises_kb(
    callback_data: PydanticObjectId
) -> types.InlineKeyboardMarkup:
    button = []
    exc = await coll_exc.find_one({"_id": callback_data})
    if exc.get("Упражнения"):
        for res in exc["Упражнения"].keys():
            button += [[types.InlineKeyboardButton(
                text=f"💪 {res}",
                callback_data=ExcercisesCallback(
                    obj=callback_data,
                    exc_name=res).pack()
            )]]
    button += [[types.InlineKeyboardButton(
        text='✅ Добавить упражнение',
        callback_data=ExcercisesAddCallback(
            obj=callback_data).pack()
        )],
        [types.InlineKeyboardButton(
            text='🏁 Завершить тренировку',
            callback_data="EndTraining"
        )]
        ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=button)
    return keyboard


async def muscle_group_kb() -> types.InlineKeyboardMarkup:
    button = []
    async for res in coll_exc.find().sort("Группа мышц"):
        button += [[types.InlineKeyboardButton(
            text=f"💪 {res['Группа мышц']}",
            callback_data=MuscleGroupCallback(
                obj=res['_id']).pack()
        )]]
    button += [[types.InlineKeyboardButton(
            text='🏁 Завершить тренировку',
            callback_data="EndTraining"
        )]
        ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=button)
    return keyboard


async def history_kb() -> types.InlineKeyboardMarkup:
    cursor = coll_train.find()
    button = []
    for res in await cursor.to_list(5):
        button += [[types.InlineKeyboardButton(
            text=f'''Тренировка {
                datetime.strptime(res["дата"], "%Y-%m-%d").strftime("%d %B %y")
                }''',
            callback_data=TrainingCallback(
                obj=res['_id']).pack()
        )]]
    button += [[types.InlineKeyboardButton(
            text='Ввести дату вручную',
            callback_data="InputDate"
        )],
            [types.InlineKeyboardButton(
                text="Вернуться в главное меню",
                callback_data="MainMenu"
            )]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=button)
    return keyboard


async def exc_history_kb(obj: PydanticObjectId) -> types.InlineKeyboardMarkup:
    button = []
    res = await coll_train.find_one({"_id": obj})
    if res.get("упражнение"):
        for exc in res["упражнение"]:
            button += [[types.InlineKeyboardButton(
                text=f"💪 {exc}",
                callback_data=ExcHistoryCallback(
                    obj=obj,
                    exc_name=exc).pack()
            )]]
    button += [[types.InlineKeyboardButton(
        text='🔙 Вернуться назад',
        callback_data="TrainHistory"
        )]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=button)
    return keyboard


def back_history_kb(obj: PydanticObjectId) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(
            text='Вернуться к списку упражнений',
            callback_data=TrainingCallback(
                obj=obj).pack()
        )],
            [types.InlineKeyboardButton(
                text="Вернуться в главное меню",
                callback_data="MainMenu"
            )]
        ])
    return keyboard


def cancel_input_kb() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(
            text='Вернуться в главное меню',
            callback_data="CancelInputDate"
        )]]
    )
    return keyboard


def choice_info(
    obj: PydanticObjectId, name: str
) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(
            text='Изменить доп. информацию',
            callback_data=ExcersisesInfoCallback(
                obj=obj, exc_name=name).pack()
        )],
            [types.InlineKeyboardButton(
                text="Внести повторения",
                callback_data=ExcersisesSetsCallback(
                    obj=obj, exc_name=name).pack()
            )]])
    return keyboard


def cancel_info() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(
            text='Отмена изменения',
            callback_data="CancelInfo"
        )]]
    )
    return keyboard
