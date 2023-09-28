from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db import coll_exc
from excercises import choice_excercises
from my_keyboard import ExcercisesAddCallback, cancel_kb


add_exc = Router()


class Excercises(StatesGroup):
    obj = State()
    name = State()
    info = State()


@add_exc.callback_query(ExcercisesAddCallback.filter())
async def add_excercises(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ExcercisesAddCallback
):
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        text='Введите название упражнения',
        reply_markup=cancel_kb()
    )
    await state.update_data(obj=callback_data.obj)
    await state.set_state(Excercises.name)


@add_exc.message(Excercises.name)
async def excercises_add_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Excercises.info)
    await message.answer(
        text='Введите описание к упражнению',
        reply_markup=cancel_kb()
    )


@add_exc.message(Excercises.info)
async def excersises_add_description(
    message: types.Message, state: FSMContext
):
    await state.update_data(info=message.text)
    data = await state.get_data()
    await coll_exc.update_one(
        {"_id": data["obj"]},
        {"$set": {f"Упражнения.{data['name']}": data["info"]}}
    )
    await message.answer(
        text=f'Упражнение: "{data["name"]}" добавлено в список'
    )
    await state.clear()
    await choice_excercises(message, data["obj"])


@add_exc.callback_query(F.data == "CancelAddExcercises")
async def cancel_add_excercises(
    callback: types.CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    await state.clear()
    await callback.message.answer(
        text="Действие отменено")
    await choice_excercises(callback.message, data['obj'])
