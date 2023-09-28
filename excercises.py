from datetime import date

from aiogram import F, Router, types
# from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from beanie import PydanticObjectId

from db import coll_exc, coll_train
from my_keyboard import (
    ExcercisesCallback, MuscleGroupCallback, ExcersisesInfoCallback,
    ExcersisesSetsCallback, cancel_ex_kb, excercises_kb, muscle_group_kb,
    start_kb, choice_info, cancel_info)
from utils import merge_dict


rp = Router()


class ExcercisesSet(StatesGroup):
    reps = State()
    info_reps = State()
    exc_name = State()
    exc_id = State()


class ExcersisesInfo(StatesGroup):
    id = State()
    name = State()
    info = State()


async def choice_excercises(
    message: types.Message, callback_data: PydanticObjectId
):
    await message.answer(
        text='Выберите упражнение',
        reply_markup=await excercises_kb(callback_data)
    )


async def choice_muscle_group(message: types.Message):
    await message.answer(
        text='Выберите группу мышц',
        reply_markup=await muscle_group_kb()
    )


async def start_excercises(
    message: types.Message, obj: PydanticObjectId, name: str
):
    res = await coll_exc.find_one({"_id": obj})
    await message.answer(
        text=f'Начинаем упражнение: {name}\n' +
        f'''Дополнительная информация: {
            res["Упражнения"][name]}''',
        reply_markup=choice_info(obj, name)
    )


@rp.callback_query(F.data == "TrainStart")
async def train_start(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        'Тренировка началась')
    if not await coll_train.find_one({"дата": date.today().isoformat()}):
        await coll_train.insert_one({"дата": date.today().isoformat()})
    await choice_muscle_group(callback.message)


@rp.callback_query(MuscleGroupCallback.filter())
async def muscle_group(
    callback: types.CallbackQuery,
    callback_data: MuscleGroupCallback
):
    await callback.message.edit_reply_markup()
    await choice_excercises(callback.message, callback_data.obj)


@rp.callback_query(ExcercisesCallback.filter())
async def excercises_info(
    callback: types.CallbackQuery,
    callback_data: ExcercisesCallback
):
    await callback.message.edit_reply_markup()
    await start_excercises(
        callback.message, callback_data.obj,
        callback_data.exc_name)


@rp.callback_query(ExcersisesInfoCallback.filter())
async def change_input_info(
    callback: types.CallbackQuery,
    callback_data: ExcersisesInfoCallback,
    state: FSMContext
):
    await callback.message.edit_reply_markup()
    await state.set_state(ExcersisesInfo.info)
    await callback.message.answer(
        text='Введите новую информацию',
        reply_markup=cancel_info()
    )
    await state.update_data(
        id=callback_data.obj,
        name=callback_data.exc_name
    )


@rp.message(ExcersisesInfo.info)
async def change_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await coll_exc.update_one(
        {"_id": data["id"]},
        {"$set": {f'Упражнения.{data["name"]}': message.text}}
    )
    await message.answer(
        text='Изменения внесены'
    )
    await state.clear()
    await start_excercises(message, data["id"], data["name"])


@rp.callback_query(F.data == "CancelInfo")
async def cancel_change_info(
    callback: types.CallbackQuery,
    state: FSMContext
):
    await callback.message.edit_reply_markup()
    data = await state.get_data()
    await state.clear()
    await start_excercises(callback.message, data["id"], data["name"])


@rp.callback_query(ExcersisesSetsCallback.filter())
async def excersises_sets(
    callback: types.CallbackQuery,
    callback_data: ExcersisesSetsCallback,
    state: FSMContext
):
    await callback.message.answer(
        text='Введите количество повторений',
        reply_markup=cancel_ex_kb()
    )
    await state.update_data(
        exc_id=callback_data.obj,
        exc_name=callback_data.exc_name
        )
    await state.set_state(ExcercisesSet.reps)


@rp.message(ExcercisesSet.reps)
async def set_reps(message: types.Message, state: FSMContext):
    res = await state.get_data()
    if res.get('reps'):
        await state.update_data(reps=res['reps']+[message.text])
    else:
        await state.update_data(reps=[message.text])
    await message.answer(
        text='Введите вес и доп. информацию'
    )
    await state.set_state(ExcercisesSet.info_reps)


@rp.message(ExcercisesSet.info_reps)
async def info_rep(message: types.Message, state: FSMContext):
    res = await state.get_data()
    if res.get('info_reps'):
        await state.update_data(info_reps=res['info_reps']+[message.text])
    else:
        await state.update_data(info_reps=[message.text])
    await state.set_state(ExcercisesSet.reps)
    await message.answer(
        text='Введите количество повторений',
        reply_markup=cancel_ex_kb()
    )


@rp.callback_query(F.data == "CancelExcercises")
async def cancel_set_excesises(
    callback: types.CallbackQuery,
    state: FSMContext
):
    res = await state.get_data()
    if res.get("reps"):
        sets = merge_dict(res["reps"], res["info_reps"])
        coll_train.update_one(
            {"дата": date.today().isoformat()},
            {"$set": {f"упражнение.{res['exc_name']}": {"подходы": sets}}}
        )
    await state.clear()
    await callback.message.answer(
        text='Упражнение закончено'
    )
    await choice_muscle_group(callback.message)


@rp.callback_query(F.data == "EndTraining")
async def end_training(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        text='Отлично потренировались!',
        reply_markup=start_kb()
    )
