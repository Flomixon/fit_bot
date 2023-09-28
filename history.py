from datetime import datetime

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from my_keyboard import (
    TrainingCallback, ExcHistoryCallback, history_kb,
    exc_history_kb, back_history_kb, cancel_input_kb)
from db import coll_train
from utils import main_menu


hi = Router()


class InputDate(StatesGroup):
    date = State()


@hi.callback_query(F.data == "TrainHistory")
async def start_history(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        text='Выберите тренировку',
        reply_markup=await history_kb()
    )


@hi.callback_query(F.data == "InputDate")
async def input_date(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(InputDate.date)
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        text="Введите дату числами в формате: день месяц год",
        reply_markup=cancel_input_kb()
    )


@hi.message(InputDate.date)
async def input_history(message: types.Message, state: FSMContext):
    '''Если нет тренировки направить ответ. Иначе обработать тренировку'''
    try:
        dat = datetime.strptime(message.text, "%d %m %y")
        if message.reply_markup:
            await message.edit_reply_markup()
        exc = await coll_train.find_one({"дата": dat.date().isoformat()})
        if not exc:
            await message.answer(
                text="В этот день не было тренировок. Попробуйте другую дату",
                reply_markup=cancel_input_kb()
            )
        else:
            await state.clear()
            await message.answer(
                text='Выберите упражнение',
                reply_markup=await exc_history_kb(exc["_id"])
            )
    except ValueError:
        await message.answer(
            text='Дата введена в неверном формате',
            reply_markup=cancel_input_kb()
        )


@hi.callback_query(F.data == "CancelInputDate")
async def cancel_input(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()
    await state.clear()
    await main_menu(callback.message)


@hi.callback_query(TrainingCallback.filter())
async def get_excercises(
    callback: types.CallbackQuery,
    callback_data: TrainingCallback
):
    '''Вернуть список упражнений'''
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        text='Выберите упражнение',
        reply_markup=await exc_history_kb(callback_data.obj)
    )


@hi.callback_query(ExcHistoryCallback.filter())
async def show_history_exc(
    callback: types.CallbackQuery,
    callback_data: ExcHistoryCallback
):
    await callback.message.edit_reply_markup()
    exc = await coll_train.find_one({"_id": callback_data.obj})
    ans = []
    for res in exc["упражнение"][callback_data.exc_name]["подходы"]:
        sets = exc["упражнение"][callback_data.exc_name]["подходы"][res]
        ans += [f'''{res}:
Колличество повторений: {sets["Колличество повторений"]}
Вес и доп. информация: {sets["Вес и доп. информация"]}''']
    await callback.message.answer(
        text="\n".join(ans),
        reply_markup=back_history_kb(callback_data.obj)
    )
