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
    sec = await db.get_section_by_id(sec_id)
    cat_id = sec[1]
    sections = await db.get_sections_by_category(cat_id)
    await call.message.edit_text("📋 Bo'limni tanlang:", reply_markup=sections_kb(sections, cat_id))

async def start_test_cb(call: types.CallbackQuery, state: FSMContext):
    sec_id = int(call.data.split("_")[2])
    questions = await db.get_questions_by_section(sec_id)
    if len(questions) < 1:
        await call.answer("⚠️ Bu bo'limda savollar yo'q!", show_alert=True)
        return
    questions = list(questions)
    random.shuffle(questions)
    questions = questions[:25]
    await state.set_state(TestStates.in_test)
    await state.update_data(questions=questions, current_q=0, correct=0, sec_id=sec_id, answers=[])
    await send_question(call.message, state, edit=True)

async def send_question(message: types.Message, state: FSMContext, edit=False):
    data = await state.get_data()
    questions = data["questions"]
    idx = data["current_q"]
    if idx >= len(questions):
        await finish_test(message, state)
        return
    q = questions[idx]
    _, sec_id, text, a, b, c, d, correct, _ = q
    total = len(questions)
    progress = "▓" * (idx + 1) + "░" * (total - idx - 1)
    msg_text = (
        f"📊 <b>{idx + 1}/{total}</b>  {progress}\n\n"
        f"❓ <b>{text}</b>\n\n"
        f"🅰️ {a}\n🅱️ {b}\n🅲 {c}\n🅳 {d}"
    )
    if edit:
        try:
            await message.edit_text(msg_text, reply_markup=answer_kb(idx))
        except:
            await message.answer(msg_text, reply_markup=answer_kb(idx))
    else:
        await message.answer(msg_text, reply_markup=answer_kb(idx))

async def answer_cb(call: types.CallbackQuery, state: FSMContext):
    parts = call.data.split("_")
    q_idx = int(parts[1])
    chosen = parts[2]
    data = await state.get_data()
    if data.get("current_q") != q_idx:
        await call.answer("Bu savol allaqachon javob berilgan!", show_alert=True)
        return
    questions = data["questions"]
    q = questions[q_idx]
    correct_answer = q[7]
    is_correct = chosen == correct_answer
    correct_count = data["correct"] + (1 if is_correct else 0)
    answers = data.get("answers", [])
    answers.append({"q_idx": q_idx, "chosen": chosen, "correct": correct_answer, "is_correct": is_correct})
    await state.update_data(current_q=q_idx + 1, correct=correct_count, answers=answers)
    if is_correct:
        await call.answer("✅ To'g'ri!", show_alert=False)
    else:
        await call.answer(f"❌ Noto'g'ri! To'g'ri javob: {correct_answer}", show_alert=True)
    await send_question(call.message, state, edit=True)

async def finish_test_cb(call: types.CallbackQuery, state: FSMContext):
    await finish_test(call.message, state)

async def finish_test(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data.get("questions", [])
    correct = data.get("correct", 0)
    sec_id = data.get("sec_id")
    total = len(questions)
    await state.finish()
    if total == 0:
        await message.answer("Test ma'lumotlari topilmadi.")
        return
    score = round((correct / total) * 100, 1)
    user_id = message.chat.id
    await db.save_test_result(user_id, sec_id, correct, total)
    if score >= 90:
        grade = "🥇 A'lo"; comment = "Ajoyib natija! Zo'rsiz!"
    elif score >= 75:
        grade = "🥈 Yaxshi"; comment = "Yaxshi natija, davom eting!"
    elif score >= 55:
        grade = "🥉 Qoniqarli"; comment = "Ko'proq mashq kerak."
    else:
        grade = "❌ Qoniqarsiz"; comment = "Ko'proq o'qish kerak!"
    filled = int(score / 5)
    bar = "█" * filled + "░" * (20 - filled)
    try:
        await message.edit_text(
            f"🏁 <b>Test yakunlandi!</b>\n\n"
            f"📊 Natija: <b>{correct}/{total}</b>\n"
            f"💯 Ball: <b>{score}%</b>\n"
            f"[{bar}]\n\n"
            f"🎖 Baho: {grade}\n💬 {comment}",
            reply_markup=result_kb(sec_id)
        )
    except:
        await message.answer(
            f"🏁 <b>Test yakunlandi!</b>\n\n"
            f"📊 Natija: <b>{correct}/{total}</b>\n"
            f"💯 Ball: <b>{score}%</b>\n"
            f"[{bar}]\n\n"
            f"🎖 Baho: {grade}\n💬 {comment}",
            reply_markup=result_kb(sec_id)
        )

async def rating_cb(call: types.CallbackQuery):
    sec_id = int(call.data.split("_")[1])
    sec = await db.get_section_by_id(sec_id)
    results = await db.get_top_results(sec_id, 10)
    if not results:
        await call.answer("Hali natijalar yo'q!", show_alert=True)
        return
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    text = f"🏆 <b>{sec[2]} - TOP 10</b>\n\n"
    for i, r in enumerate(results):
        score, correct, total, name, date = r
        text += f"{medals[i]} <b>{name}</b>: {score}% ({correct}/{total})\n"
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"sec_{sec_id}"))
    await call.message.edit_text(text, reply_markup=kb)

def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=["start"], state="*")
    dp.register_message_handler(categories_handler, text="📚 Fanlar", state="*")
    dp.register_message_handler(my_results_handler, text="📊 Natijalarim", state="*")
    dp.register_message_handler(info_handler, text="ℹ️ Ma'lumot", state="*")
    dp.register_callback_query_handler(back_main_cb, text="back_main", state="*")
    dp.register_callback_query_handler(back_cats_cb, text="back_cats", state="*")
    dp.register_callback_query_handler(category_cb, lambda c: c.data.startswith("cat_"), state="*")
    dp.register_callback_query_handler(section_cb, lambda c: c.data.startswith("sec_"), state="*")
    dp.register_callback_query_handler(back_sec_cb, lambda c: c.data.startswith("back_sec_"), state="*")
    dp.register_callback_query_handler(start_test_cb, lambda c: c.data.startswith("start_test_"), state="*")
    dp.register_callback_query_handler(answer_cb, lambda c: c.data.startswith("ans_"), state=TestStates.in_test)
    dp.register_callback_query_handler(finish_test_cb, text="finish_test", state=TestStates.in_test)
    dp.register_callback_query_handler(rating_cb, lambda c: c.data.startswith("rating_"), state="*")
