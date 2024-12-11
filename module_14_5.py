import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import get_all_products
from crud_functions import add_user
from crud_functions import is_included

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()

kb = ReplyKeyboardMarkup(resize_keyboard=True)
bc = KeyboardButton(text="Рассчитать")
bi = KeyboardButton(text="Информация")
bu = KeyboardButton(text="Купить")
re = KeyboardButton(text='Регистрация')

kb.add(bc, bi, bu, re)

inline_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
    InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas'))

inline_pkb = InlineKeyboardMarkup().add(
InlineKeyboardButton(text='Product1', callback_data='product_buying_1'),
    InlineKeyboardButton(text='Product2', callback_data='product_buying_1'),
        InlineKeyboardButton(text='Product3', callback_data='product_buying_1'),
        InlineKeyboardButton(text='Product4', callback_data='product_buying_1'))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью !              \n\n"
                         "Расчитываю приблизительную норму калорий  для женщин          \n"
                         " и продаю суплимены диеты                                 \n\n\n"
                         "Для получения информации о боте нажмите кнопку 'Информация'  \n"
                         "Для расчета нормы колорий нажмите кнопку 'Рассчитать'        \n"
                         "Для покупки суплиментов диеты нажмите кнопку 'Купить'         \n\n\n"
                         "         Зарегистрируйся пожалуйста !!!          \n\n\n",
                         reply_markup=kb)
@dp.message_handler(text='Информация')
async def set_age(message: types.Message):
    await message.answer("Я могу рассказать Вам подробнее об этом боте, но я не думаю, что это будет Вам интересно ))) \n\n"
                              "Быстрее нажимайте кнопку 'Рассчитать' или 'Купить'- это интереснее !!!", reply_markup=kb)

@dp.message_handler(text='Рассчитать')
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=inline_kb)

@dp.message_handler(text='Регистрация')
async def start_registration(message: types.Message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()
@dp.message_handler(text='Купить')
async def get_buying_list(message):
    products = get_all_products()
    for product in products:
        await message.answer(
            f"Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}")
        with open(f"Product{product[0]}.JPEG", 'rb') as photo:
            await message.answer_photo(photo)
    await message.answer("Выберите продукт для покупки:", reply_markup=inline_pkb)

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await message.answer("Введите свой рост:")
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=int(message.text))
    await message.answer("Введите свой вес:")
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()
    age = data['age']
    growth = data['growth']
    weight = data['weight']

    calories = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.answer(f"Ваша приблизительная норма калорий: {calories}")
    await state.finish()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message: types.Message, state: FSMContext):
    username = message.text
    if is_included(username):
        await message.answer("Пользователь существует, введите другое имя")
        return await RegistrationState.username.set()
    await state.update_data(username=username)
    await message.answer("Введите свой email:")
    await RegistrationState.next()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Введите свой возраст:")
    await RegistrationState.next()

@dp.message_handler(state=RegistrationState.age)
async def set_age_and_register(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    user_data = await state.get_data()
    add_user(user_data['username'], user_data['email'], user_data['age'])
    await message.answer("Регистрация успешно завершена!")
    await state.finish()

@dp.callback_query_handler(text="product_buying_1")
async def handle_product_buying(call: types.CallbackQuery):
    await call.message.answer("Вы успешно приобрели продукт!")

@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()

@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer(
    "Упрошенная формула Миффлина-Сан Жеора для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161.\n")
@dp.message_handler()
async def all_messages(message: types.Message):
    await message.answer("Введите команду /start, чтобы начать общение.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)