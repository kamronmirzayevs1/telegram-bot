import random
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import database as db
from keyboards import (
    main_menu_kb, categories_kb, sections_kb,
    start_test_kb, answer_kb, result_kb
)

class TestStates(StatesGroup):
    in_test = State()

async def start_handler(msg: types.Message, state: FSMContext):
    await state.finish()
    await db.add_user(msg.from_user.id, msg.from_user.full_name, msg.from_user.username or "")
    await msg.answer(
        f"👋 Assalomu alaykum, <b>{msg.from_user.full_name}</b>!\n\n"
        "🎓 <b>Test Platformasiga</b> xush kelibsiz!\n\n"
        "📚 Turli fanlar bo'yicha testlarni ishlashingiz mumkin.\n"
        "Har bir bo'limda <b>25 ta savol</b> mavjud.\n\n"
        "Quyidagi menyudan boshlang 👇",
        reply_markup=main_menu_kb()
    )

async def info_handler(msg: types.Message):
    users_count = await db.get_users_count()
    tests_count = await db.get_total_tests_count()
    await msg.answer(
        "ℹ️ <b>Bot haqida ma'lumot</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users_count}</b>\n"
        f"✅ Ishlangan testlar: <b>{tests_count}</b>\n\n"
        "📝 Har bir bo'limda 25 ta savol\n"
        "🏆 Har bir test uchun ball saqlanadi"
    )

async def categories_handler(msg: types.Message, state: FSMContext):
    await state.finish()
    cats = await db.get_all_categories()
    if not cats:
        await msg.answer("⚠️ Hozircha kategoriyalar mavjud emas.")
        return
    await msg.answer("📚 <b>Fanlar ro'yxati</b>\n\nFanni tanlang:", reply_markup=categories_kb(cats))

async def my_results_handler(msg: types.Message):
    results = await db.get_user_results(msg.from_user.id)
    if not results:
        await msg.answer("📊 Siz hali hech qanday test ishlamagansiz.")
        return
    text = "📊 <b>Oxirgi 10 ta natijangiz:</b>\n\n"
    for r in results:
        _, user_id, sec_id, correct, total, score, finished_at, sec_name, cat_name = r
        date = finished_at[:10] if finished_at else ""
        text += f"📝 <b>{sec_name}</b> ({cat_name})\n"
        text += f"   💯 {score}% | ✅ {correct}/{total} | 📅 {date}\n\n"
    await msg.answer(text)

async def category_cb(call: types.CallbackQuery, state: FSMContext):
    cat_id = int(call.data.split("_")[1])
    cat = await db.get_category_by_id(cat_id)
    sections = await db.get_sections_by_category(cat_id)
    if not sections:
        await call.answer("⚠️ Bu kategoriyada hali bo'limlar yo'q!", show_alert=True)
        return
    await call.message.edit_text(
        f"{cat[2]} <b>{cat[1]}</b>\n\n"
        f"📋 Bo'limlar soni: <b>{len(sections)}</b>\n\nBo'limni tanlang:",
        reply_markup=sections_kb(sections, cat_id)
    )

async def back_cats_cb(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    cats = await db.get_all_categories()
    if not cats:
        await call.message.edit_text("⚠️ Hozircha kategoriyalar mavjud emas.")
        return
    await call.message.edit_text("📚 <b>Fanlar ro'yxati</b>\n\nFanni tanlang:", reply_markup=categories_kb(cats))

async def back_main_cb(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer("🏠 Bosh menyuga qaytdingiz.", reply_markup=main_menu_kb())

async def section_cb(call: types.CallbackQuery):
    sec_id = int(call.data.split("_")[1])
    sec = await db.get_section_by_id(sec_id)
    q_count = await db.get_questions_count(sec_id)
    status = "✅ Tayyor" if q_count >= 25 else f"⚠️ {q_count}/25 savol bor"
    await call.message.edit_text(
        f"📝 <b>{sec[2]}</b>\n\n"
        f"❓ Savollar: <b>{q_count}</b>/25\n"
        f"📌 Holat: {status}\n\n"
        "Test haqida:\n• 25 ta savol\n• A/B/C/D variantli\n• Natija foizda",
        reply_markup=start_test_kb(sec_id)
    )

async def back_sec_cb(call: types.CallbackQuery):
    sec_id = int(call.data.split("_")[2])
    sec = await
