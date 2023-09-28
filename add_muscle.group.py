from db import coll_exc, client


muscle_group = [
    'Спина', 'Ноги', 'Грудные', 'Руки', 'Плечи', 'Пресс'
]


async def ad_muscle_group():
    await coll_exc.insert_many(
        [{"Группа мышц": i} for i in muscle_group]
    )


loop = client.get_io_loop()
loop.run_until_complete(ad_muscle_group())
