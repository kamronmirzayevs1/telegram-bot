import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

import database as db
from keyboards import (
    main_menu_kb, categories_kb, sections_kb,
    start_test_kb, answer_kb, result_kb
)

router = Router()

# ===================== START =====================

@router.message(CommandStart())
async def start_handler(msg: Message, state: FSMContext):
    await state.clear()
    await db.add_user(msg.from_user.id, msg.from_user.full_name, msg.from_user.username or "")
    await msg.answer(
        f"👋 Assalomu alaykum, <b>{msg.from_user.full_name}</b>!\n\n"
        "🎓 <b>Test Platformasiga</b> xush kelibsiz!\n\n"
        "📚 Bu yerda siz turli fanlar bo'yicha testlarni ishlashingiz mumkin.\n"
        "Har bir bo'limda <b>25 ta savol</b> mavjud.\n\n"
        "Quyidagi menyudan boshlang 👇",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )

@router.message(F.text == "ℹ️ Ma'lumot")
async def info_handler(msg: Message):
    users_count = await db.get_users_count()
    tests_count = await db.get_total_tests_count()
    await msg.answer(
        "ℹ️ <b>Bot haqida ma'lumot</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users_count}</b>\n"
        f"✅ Ishlangan testlar: <b>{tests_count}</b>\n\n"
        "📝 Har bir bo'limda 25 ta savol mavjud\n"
        "🏆 Har bir test uchun ball saqlanadi\n"
        "📊 Natijalaringizni kuzatib boring!",
        parse_mode="HTML"
    )

# ===================== FANLAR =====================

@router.message(F.text == "📚 Fanlar")
async def categories_handler(msg: Message, state: FSMContext):
    await state.clear()
    cats = await db.get_all_categories()
    if not cats:
        await msg.answer("⚠️ Hozircha kategoriyalar mavjud emas.")
        return
    await msg.answer("📚 <b>Fanlar ro'yxati</b>\n\nQuyidagi fanlardan birini tanlang:", 
                     reply_markup=categories_kb(cats), parse_mode="HTML")

@router.callback_query(F.data == "back_cats")
async def back_to_cats(call: CallbackQuery, state: FSMContext):
    await state.clear()
    cats = await db.get_all_categories()
    if not cats:
        await call.message.edit_text("⚠️ Hozircha kategoriyalar mavjud emas.")
        return
    await call.message.edit_text("📚 <b>Fanlar ro'yxati</b>\n\nQuyidagi fanlardan birini tanlang:", 
                                  reply_markup=categories_kb(cats), parse_mode="HTML")

@router.callback_query(F.data == "back_main")
async def back_to_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.message.answer("🏠 Bosh menyuga qaytdingiz.", reply_markup=main_menu_kb())

@router.callback_query(F.data.startswith("cat_"))
async def category_selected(call: CallbackQuery):
    cat_id = int(call.data.split("_")[1])
    cat = await db.get_category_by_id(cat_id)
    sections = await db.get_sections_by_category(cat_id)
    
    if not sections:
        await call.answer("⚠️ Bu kategoriyada hali bo'limlar yo'q!", show_alert=True)
        return
    
    await call.message.edit_text(
        f"{cat[2]} <b>{cat[1]}</b>\n\n"
        f"📋 Bo'limlar soni: <b>{len(sections)}</b>\n\n"
        "Bo'limni tanlang:",
        reply_markup=sections_kb(sections, cat_id),
        parse_mode="HTML"
    )

# ===================== BO'LIMLAR =====================

@router.callback_query(F.data.startswith("sec_"))
async def section_selected(call: CallbackQuery):
    sec_id = int(call.data.split("_")[1])
    sec = await db.get_section_by_id(sec_id)
    q_count = await db.get_questions_count(sec_id)
    
    status = "✅ Tayyor" if q_count >= 25 else f"⚠️ {q_count}/25 savol bor"
    
    await call.message.edit_text(
        f"📝 <b>{sec[2]}</b>\n\n"
        f"❓ Savollar: <b>{q_count}</b>/25\n"
        f"📌 Holat: {status}\n\n"
        "Test haqida:\n"
        "• 25 ta savol\n"
        "• Har bir savol A/B/C/D variantli\n"
        "• Natija foizda ko'rsatiladi",
        reply_markup=start_test_kb(sec_id),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("back_sec_"))
async def back_to_section(call: CallbackQuery):
    sec_id = int(call.data.split("_")[2])
    sec = await db.get_section_by_id(sec_id)
    cat_id = sec[1]
    sections = await db.get_sections_by_category(cat_id)
    await call.message.edit_text(
        "📋 Bo'limni tanlang:",
        reply_markup=sections_kb(sections, cat_id)
    )

# ===================== TEST =====================

@router.callback_query(F.data.startswith("start_test_"))
async def start_test(call: CallbackQuery, state: FSMContext):
    sec_id = int(call.data.split("_")[2])
    questions = await db.get_questions_by_section(sec_id)
    
    if len(questions) < 1:
        await call.answer("⚠️ Bu bo'limda savollar yo'q!", show_alert=True)
        return
    
    # Shuffle questions, take up to 25
    questions = list(questions)
    random.shuffle(questions)
    questions = questions[:25]
    
    await state.update_data(
        questions=questions,
        current_q=0,
        correct=0,
        sec_id=sec_id,
        answers=[]
    )
    
    await send_question(call.message, state, edit=True)

async def send_question(message: Message, state: FSMContext, edit: bool = False):
    data = await state.get_data()
    questions = data["questions"]
    idx = data["current_q"]
    
    if idx >= len(questions):
        await finish_test(message, state)
        return
    
    q = questions[idx]
    q_id, sec_id, text, a, b, c, d, correct, _ = q
    
    total = len(questions)
    progress = "▓" * (idx + 1) + "░" * (total - idx - 1)
    
    msg_text = (
        f"📊 <b>{idx + 1}/{total}</b>  {progress}\n\n"
        f"❓ <b>{text}</b>\n\n"
        f"🅰️ {a}\n"
        f"🅱️ {b}\n"
        f"🅲 {c}\n"
        f"🅳 {d}"
    )
    
    if edit:
        try:
            await message.edit_text(msg_text, reply_markup=answer_kb(idx), parse_mode="HTML")
        except:
            await message.answer(msg_text, reply_markup=answer_kb(idx), parse_mode="HTML")
    else:
        await message.answer(msg_text, reply_markup=answer_kb(idx), parse_mode="HTML")

@router.callback_query(F.data.startswith("ans_"))
async def answer_handler(call: CallbackQuery, state: FSMContext):
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
    
    await state.update_data(
        current_q=q_idx + 1,
        correct=correct_count,
        answers=answers
    )
    
    if is_correct:
        await call.answer("✅ To'g'ri!", show_alert=False)
    else:
        await call.answer(f"❌ Noto'g'ri! To'g'ri javob: {correct_answer}", show_alert=True)
    
    await send_question(call.message, state, edit=True)

@router.callback_query(F.data == "finish_test")
async def finish_test_early(call: CallbackQuery, state: FSMContext):
    await finish_test(call.message, state)

async def finish_test(message: Message, state: FSMContext):
    data = await state.get_data()
    questions = data.get("questions", [])
    correct = data.get("correct", 0)
    sec_id = data.get("sec_id")
    total = len(questions)
    
    await state.clear()
    
    if total == 0:
        await message.answer("Test ma'lumotlari topilmadi.")
        return
    
    score = round((correct / total) * 100, 1)
    
    # Save result
    from aiogram.types import Message as Msg
    user_id = message.chat.id
    await db.save_test_result(user_id, sec_id, correct, total)
    
    # Grade
    if score >= 90:
        grade = "🥇 A'lo"
        comment = "Ajoyib natija! Zo'rsiz!"
    elif score >= 75:
        grade = "🥈 Yaxshi"
        comment = "Yaxshi natija, davom eting!"
    elif score >= 55:
        grade = "🥉 Qoniqarli"
        comment = "Yaxshi, lekin ko'proq mashq kerak."
    else:
        grade = "❌ Qoniqarsiz"
        comment = "Ko'proq o'qish kerak. Harakat qiling!"
    
    # Visual bar
    filled = int(score / 5)
    bar = "█" * filled + "░" * (20 - filled)
    
    await message.edit_text(
        f"🏁 <b>Test yakunlandi!</b>\n\n"
        f"📊 Natija: <b>{correct}/{total}</b>\n"
        f"💯 Ball: <b>{score}%</b>\n"
        f"[{bar}]\n\n"
        f"🎖 Baho: {grade}\n"
        f"💬 {comment}",
        reply_markup=result_kb(sec_id),
        parse_mode="HTML"
    )

# ===================== REYTING =====================

@router.callback_query(F.data.startswith("rating_"))
async def show_rating(call: CallbackQuery):
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
    
    from keyboards import InlineKeyboardBuilder, InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder as IKB
    builder = IKB()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"sec_{sec_id}"))
    
    await call.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")

# ===================== NATIJALAR =====================

@router.message(F.text == "📊 Natijalarim")
async def my_results(msg: Message):
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
    
    await msg.answer(text, parse_mode="HTML")
