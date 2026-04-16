from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import (
    admin_main_kb, admin_categories_kb, admin_category_menu_kb,
    admin_sections_kb, admin_section_menu_kb, admin_questions_kb,
    admin_question_menu_kb, confirm_kb, main_menu_kb
)
from config import ADMIN_IDS

router = Router()

# ===================== STATES =====================

class AdminStates(StatesGroup):
    waiting_category_name = State()
    waiting_category_emoji = State()
    waiting_section_name = State()
    waiting_question_text = State()
    waiting_option_a = State()
    waiting_option_b = State()
    waiting_option_c = State()
    waiting_option_d = State()
    waiting_correct = State()
    waiting_broadcast = State()

# ===================== FILTERS =====================

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# ===================== ADMIN PANEL =====================

@router.message(Command("admin"))
async def admin_panel(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        await msg.answer("❌ Sizda admin huquqi yo'q!")
        return
    await state.clear()
    users = await db.get_users_count()
    tests = await db.get_total_tests_count()
    await msg.answer(
        f"🛠 <b>Admin Panel</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users}</b>\n"
        f"✅ Ishlangan testlar: <b>{tests}</b>\n\n"
        "Amalni tanlang:",
        reply_markup=admin_main_kb(),
        parse_mode="HTML"
    )

@router.message(F.text == "🔙 Foydalanuvchi rejimi")
async def back_to_user(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("👤 Foydalanuvchi rejimidasiz.", reply_markup=main_menu_kb())

# ===================== STATISTIKA =====================

@router.message(F.text == "📊 Statistika")
async def admin_stats(msg: Message):
    if not is_admin(msg.from_user.id):
        return
    users = await db.get_users_count()
    tests = await db.get_total_tests_count()
    cats = await db.get_all_categories_admin()
    
    total_q = 0
    total_sec = 0
    for cat in cats:
        secs = await db.get_sections_by_category_admin(cat[0])
        total_sec += len(secs)
        for sec in secs:
            q_count = await db.get_questions_count(sec[0])
            total_q += q_count
    
    await msg.answer(
        f"📊 <b>Bot Statistikasi</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users}</b>\n"
        f"✅ Ishlangan testlar: <b>{tests}</b>\n"
        f"📂 Kategoriyalar: <b>{len(cats)}</b>\n"
        f"📝 Bo'limlar: <b>{total_sec}</b>\n"
        f"❓ Savollar: <b>{total_q}</b>",
        parse_mode="HTML"
    )

# ===================== FOYDALANUVCHILAR =====================

@router.message(F.text == "👤 Foydalanuvchilar")
async def admin_users(msg: Message):
    if not is_admin(msg.from_user.id):
        return
    users = await db.get_all_users()
    if not users:
        await msg.answer("Foydalanuvchilar yo'q.")
        return
    
    text = f"👥 <b>Foydalanuvchilar ({len(users)} ta)</b>\n\n"
    for u in users[:20]:
        uid, tg_id, name, username, created = u
        uname = f"@{username}" if username else "—"
        text += f"• <b>{name}</b> ({uname}) - ID: <code>{tg_id}</code>\n"
    
    if len(users) > 20:
        text += f"\n... va yana {len(users) - 20} ta"
    
    await msg.answer(text, parse_mode="HTML")

# ===================== BROADCAST =====================

@router.message(F.text == "📨 Xabar yuborish")
async def broadcast_start(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    await state.set_state(AdminStates.waiting_broadcast)
    await msg.answer("📨 Barcha foydalanuvchilarga yubormoqchi bo'lgan xabarni kiriting:\n\n(Bekor qilish uchun /cancel)")

@router.message(AdminStates.waiting_broadcast)
async def broadcast_send(msg: Message, state: FSMContext):
    await state.clear()
    users = await db.get_all_users()
    sent = 0
    failed = 0
    for u in users:
        try:
            await msg.bot.send_message(u[1], f"📢 <b>Admin xabari:</b>\n\n{msg.text}", parse_mode="HTML")
            sent += 1
        except:
            failed += 1
    await msg.answer(f"✅ Xabar yuborildi!\n📤 Yuborildi: {sent}\n❌ Yuborilmadi: {failed}")

# ===================== KATEGORIYALAR =====================

@router.message(F.text == "📂 Kategoriyalar")
async def admin_categories(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    await state.clear()
    cats = await db.get_all_categories_admin()
    await msg.answer(
        f"📂 <b>Kategoriyalar</b> ({len(cats)} ta)\n\nKategoriyani tanlang:",
        reply_markup=admin_categories_kb(cats),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "adm_back_cats")
async def adm_back_cats(call: CallbackQuery, state: FSMContext):
    await state.clear()
    cats = await db.get_all_categories_admin()
    await call.message.edit_text(
        f"📂 <b>Kategoriyalar</b> ({len(cats)} ta)\n\nKategoriyani tanlang:",
        reply_markup=admin_categories_kb(cats),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "adm_add_cat")
async def adm_add_category_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_category_name)
    await call.message.edit_text("📂 Yangi kategoriya nomini kiriting:\n\n(Masalan: Matematika)")

@router.message(AdminStates.waiting_category_name)
async def adm_add_category_name(msg: Message, state: FSMContext):
    await state.update_data(cat_name=msg.text)
    await state.set_state(AdminStates.waiting_category_emoji)
    await msg.answer("Kategoriya uchun emoji kiriting:\n(Masalan: 📐 yoki 🧪)\n\nDefault: 📚")

@router.message(AdminStates.waiting_category_emoji)
async def adm_add_category_emoji(msg: Message, state: FSMContext):
    data = await state.get_data()
    emoji = msg.text.strip() if msg.text else "📚"
    await db.add_category(data["cat_name"], emoji)
    await state.clear()
    cats = await db.get_all_categories_admin()
    await msg.answer(
        f"✅ '{data['cat_name']}' kategoriyasi qo'shildi!\n\n📂 Kategoriyalar:",
        reply_markup=admin_categories_kb(cats)
    )

@router.callback_query(F.data.startswith("adm_cat_"))
async def adm_category_menu(call: CallbackQuery):
    cat_id = int(call.data.split("_")[2])
    cat = await db.get_category_by_id(cat_id)
    secs = await db.get_sections_by_category_admin(cat_id)
    await call.message.edit_text(
        f"{cat[2]} <b>{cat[1]}</b>\n\n"
        f"📋 Bo'limlar soni: <b>{len(secs)}</b>",
        reply_markup=admin_category_menu_kb(cat_id),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("adm_del_cat_"))
async def adm_confirm_del_cat(call: CallbackQuery):
    cat_id = int(call.data.split("_")[3])
    await call.message.edit_text(
        "⚠️ Kategoriyani o'chirsangiz, barcha bo'limlar va savollar ham o'chadi!\n\nRostan o'chirmoqchimisiz?",
        reply_markup=confirm_kb(f"delcat_{cat_id}")
    )

@router.callback_query(F.data.startswith("confirm_delcat_"))
async def adm_delete_category(call: CallbackQuery):
    cat_id = int(call.data.split("_")[2])
    await db.delete_category(cat_id)
    cats = await db.get_all_categories_admin()
    await call.message.edit_text(
        "✅ Kategoriya o'chirildi!\n\n📂 Kategoriyalar:",
        reply_markup=admin_categories_kb(cats)
    )

@router.callback_query(F.data == "cancel_action")
async def cancel_action(call: CallbackQuery):
    await call.message.delete()
    await call.answer("Bekor qilindi.")

# ===================== BO'LIMLAR =====================

@router.callback_query(F.data.startswith("adm_sections_"))
async def adm_sections(call: CallbackQuery):
    cat_id = int(call.data.split("_")[2])
    secs = await db.get_sections_by_category_admin(cat_id)
    await call.message.edit_text(
        f"📝 <b>Bo'limlar</b> ({len(secs)} ta)\n\nBo'limni tanlang:",
        reply_markup=admin_sections_kb(secs, cat_id),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("adm_add_sec_"))
async def adm_add_section_start(call: CallbackQuery, state: FSMContext):
    cat_id = int(call.data.split("_")[3])
    await state.update_data(cat_id=cat_id)
    await state.set_state(AdminStates.waiting_section_name)
    await call.message.edit_text("📝 Yangi bo'lim nomini kiriting:\n\n(Masalan: 1-variant yoki Algebra)")

@router.message(AdminStates.waiting_section_name)
async def adm_add_section_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    cat_id = data["cat_id"]
    await db.add_section(cat_id, msg.text)
    await state.clear()
    secs = await db.get_sections_by_category_admin(cat_id)
    await msg.answer(
        f"✅ '{msg.text}' bo'limi qo'shildi!\n\n📝 Bo'limlar:",
        reply_markup=admin_sections_kb(secs, cat_id)
    )

@router.callback_query(F.data.startswith("adm_sec_"))
async def adm_section_menu(call: CallbackQuery):
    sec_id = int(call.data.split("_")[2])
    sec = await db.get_section_by_id(sec_id)
    q_count = await db.get_questions_count(sec_id)
    await call.message.edit_text(
        f"📝 <b>{sec[2]}</b>\n\n"
        f"❓ Savollar: <b>{q_count}/25</b>",
        reply_markup=admin_section_menu_kb(sec_id, q_count),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("adm_back_secs_"))
async def adm_back_to_secs(call: CallbackQuery):
    sec_id = int(call.data.split("_")[3])
    sec = await db.get_section_by_id(sec_id)
    cat_id = sec[1]
    secs = await db.get_sections_by_category_admin(cat_id)
    await call.message.edit_text(
        f"📝 <b>Bo'limlar</b> ({len(secs)} ta)",
        reply_markup=admin_sections_kb(secs, cat_id),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("adm_del_sec_"))
async def adm_confirm_del_sec(call: CallbackQuery):
    sec_id = int(call.data.split("_")[3])
    await call.message.edit_text(
        "⚠️ Bo'limni o'chirsangiz, barcha savollar ham o'chadi!\n\nRostan o'chirmoqchimisiz?",
        reply_markup=confirm_kb(f"delsec_{sec_id}")
    )

@router.callback_query(F.data.startswith("confirm_delsec_"))
async def adm_delete_section(call: CallbackQuery):
    sec_id = int(call.data.split("_")[2])
    await db.delete_section(sec_id)
    await call.message.edit_text("✅ Bo'lim o'chirildi!")

# ===================== SAVOLLAR =====================

@router.callback_query(F.data.startswith("adm_questions_"))
async def adm_questions_list(call: CallbackQuery):
    sec_id = int(call.data.split("_")[2])
    questions = await db.get_questions_by_section(sec_id)
    await call.message.edit_text(
        f"❓ <b>Savollar</b> ({len(questions)}/25)\n\nSavolni tanlang:",
        reply_markup=admin_questions_kb(questions, sec_id),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("adm_q_"))
async def adm_question_detail(call: CallbackQuery):
    q_id = int(call.data.split("_")[2])
    q = await db.get_question_by_id(q_id)
    if not q:
        await call.answer("Savol topilmadi!", show_alert=True)
        return
    
    q_id, sec_id, text, a, b, c, d, correct, _ = q
    
    await call.message.edit_text(
        f"❓ <b>Savol #{q_id}</b>\n\n"
        f"{text}\n\n"
        f"🅰️ {a}\n"
        f"🅱️ {b}\n"
        f"🅲 {c}\n"
        f"🅳 {d}\n\n"
        f"✅ To'g'ri javob: <b>{correct}</b>",
        reply_markup=admin_question_menu_kb(q_id, sec_id),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("adm_add_q_"))
async def adm_add_question_start(call: CallbackQuery, state: FSMContext):
    sec_id = int(call.data.split("_")[3])
    q_count = await db.get_questions_count(sec_id)
    
    if q_count >= 25:
        await call.answer("⚠️ Bu bo'limda allaqachon 25 ta savol bor!", show_alert=True)
        return
    
    await state.update_data(sec_id=sec_id)
    await state.set_state(AdminStates.waiting_question_text)
    await call.message.edit_text(
        f"❓ <b>Yangi savol qo'shish</b> ({q_count + 1}/25)\n\n"
        "Savol matnini kiriting:",
        parse_mode="HTML"
    )

@router.message(AdminStates.waiting_question_text)
async def adm_q_text(msg: Message, state: FSMContext):
    await state.update_data(q_text=msg.text)
    await state.set_state(AdminStates.waiting_option_a)
    await msg.answer("🅰️ A variantini kiriting:")

@router.message(AdminStates.waiting_option_a)
async def adm_q_a(msg: Message, state: FSMContext):
    await state.update_data(option_a=msg.text)
    await state.set_state(AdminStates.waiting_option_b)
    await msg.answer("🅱️ B variantini kiriting:")

@router.message(AdminStates.waiting_option_b)
async def adm_q_b(msg: Message, state: FSMContext):
    await state.update_data(option_b=msg.text)
    await state.set_state(AdminStates.waiting_option_c)
    await msg.answer("🅲 C variantini kiriting:")

@router.message(AdminStates.waiting_option_c)
async def adm_q_c(msg: Message, state: FSMContext):
    await state.update_data(option_c=msg.text)
    await state.set_state(AdminStates.waiting_option_d)
    await msg.answer("🅳 D variantini kiriting:")

@router.message(AdminStates.waiting_option_d)
async def adm_q_d(msg: Message, state: FSMContext):
    await state.update_data(option_d=msg.text)
    await state.set_state(AdminStates.waiting_correct)
    await msg.answer(
        "✅ To'g'ri javobni kiriting:\n\n"
        "Faqat: <b>A</b>, <b>B</b>, <b>C</b> yoki <b>D</b>",
        parse_mode="HTML"
    )

@router.message(AdminStates.waiting_correct)
async def adm_q_correct(msg: Message, state: FSMContext):
    answer = msg.text.strip().upper()
    if answer not in ["A", "B", "C", "D"]:
        await msg.answer("❌ Faqat A, B, C yoki D kiriting!")
        return
    
    data = await state.get_data()
    await state.clear()
    
    await db.add_question(
        section_id=data["sec_id"],
        question_text=data["q_text"],
        option_a=data["option_a"],
        option_b=data["option_b"],
        option_c=data["option_c"],
        option_d=data["option_d"],
        correct_answer=answer
    )
    
    q_count = await db.get_questions_count(data["sec_id"])
    sec = await db.get_section_by_id(data["sec_id"])
    
    await msg.answer(
        f"✅ Savol muvaffaqiyatli qo'shildi!\n\n"
        f"📝 Bo'lim: <b>{sec[2]}</b>\n"
        f"❓ Savollar soni: <b>{q_count}/25</b>",
        reply_markup=admin_section_menu_kb(data["sec_id"], q_count),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("adm_del_q_"))
async def adm_confirm_del_q(call: CallbackQuery):
    parts = call.data.split("_")
    q_id = int(parts[3])
    sec_id = int(parts[4])
    await call.message.edit_text(
        "⚠️ Bu savolni o'chirishni tasdiqlaysizmi?",
        reply_markup=confirm_kb(f"delq_{q_id}_{sec_id}")
    )

@router.callback_query(F.data.startswith("confirm_delq_"))
async def adm_delete_question(call: CallbackQuery):
    parts = call.data.split("_")
    q_id = int(parts[2])
    sec_id = int(parts[3])
    await db.delete_question(q_id)
    questions = await db.get_questions_by_section(sec_id)
    await call.message.edit_text(
        f"✅ Savol o'chirildi!\n\n❓ Savollar ({len(questions)}/25):",
        reply_markup=admin_questions_kb(questions, sec_id)
    )

@router.message(Command("cancel"))
async def cancel_handler(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Bekor qilindi.", reply_markup=admin_main_kb())
