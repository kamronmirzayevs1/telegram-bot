from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import database as db
from keyboards import (
    admin_main_kb, admin_categories_kb, admin_category_menu_kb,
    admin_sections_kb, admin_section_menu_kb, admin_questions_kb,
    admin_question_menu_kb, confirm_kb, main_menu_kb
)
from config import ADMIN_IDS

def is_admin(user_id): return user_id in ADMIN_IDS

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

async def admin_panel(msg: types.Message, state: FSMContext):
    if not is_admin(msg.from_user.id): await msg.answer("❌ Sizda admin huquqi yo'q!"); return
    await state.finish()
    users = await db.get_users_count()
    tests = await db.get_total_tests_count()
    await msg.answer(
        f"🛠 <b>Admin Panel</b>\n\n👥 Foydalanuvchilar: <b>{users}</b>\n✅ Ishlangan testlar: <b>{tests}</b>\n\nAmalni tanlang:",
        reply_markup=admin_main_kb()
    )

async def back_to_user(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("👤 Foydalanuvchi rejimidasiz.", reply_markup=main_menu_kb())

async def admin_stats(msg: types.Message):
    if not is_admin(msg.from_user.id): return
    users = await db.get_users_count()
    tests = await db.get_total_tests_count()
    cats = await db.get_all_categories_admin()
    total_q = 0; total_sec = 0
    for cat in cats:
        secs = await db.get_sections_by_category_admin(cat[0])
        total_sec += len(secs)
        for sec in secs:
            total_q += await db.get_questions_count(sec[0])
    await msg.answer(
        f"📊 <b>Bot Statistikasi</b>\n\n👥 Foydalanuvchilar: <b>{users}</b>\n✅ Testlar: <b>{tests}</b>\n"
        f"📂 Kategoriyalar: <b>{len(cats)}</b>\n📝 Bo'limlar: <b>{total_sec}</b>\n❓ Savollar: <b>{total_q}</b>"
    )

async def admin_users(msg: types.Message):
    if not is_admin(msg.from_user.id): return
    users = await db.get_all_users()
    if not users: await msg.answer("Foydalanuvchilar yo'q."); return
    text = f"👥 <b>Foydalanuvchilar ({len(users)} ta)</b>\n\n"
    for u in users[:20]:
        uid, tg_id, name, username, created = u
        uname = f"@{username}" if username else "—"
        text += f"• <b>{name}</b> ({uname}) - <code>{tg_id}</code>\n"
    if len(users) > 20: text += f"\n... va yana {len(users)-20} ta"
    await msg.answer(text)

async def broadcast_start(msg: types.Message, state: FSMContext):
    if not is_admin(msg.from_user.id): return
    await AdminStates.waiting_broadcast.set()
    await msg.answer("📨 Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:\n(/cancel - bekor qilish)")

async def broadcast_send(msg: types.Message, state: FSMContext):
    await state.finish()
    users = await db.get_all_users()
    sent = 0; failed = 0
    for u in users:
        try:
            await msg.bot.send_message(u[1], f"📢 <b>Admin xabari:</b>\n\n{msg.text}")
            sent += 1
        except: failed += 1
    await msg.answer(f"✅ Yuborildi: {sent}\n❌ Yuborilmadi: {failed}")

async def admin_categories(msg: types.Message, state: FSMContext):
    if not is_admin(msg.from_user.id): return
    await state.finish()
    cats = await db.get_all_categories_admin()
    await msg.answer(f"📂 <b>Kategoriyalar</b> ({len(cats)} ta)", reply_markup=admin_categories_kb(cats))

async def adm_back_cats_cb(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    cats = await db.get_all_categories_admin()
    await call.message.edit_text(f"📂 <b>Kategoriyalar</b> ({len(cats)} ta)", reply_markup=admin_categories_kb(cats))

async def adm_add_cat_cb(call: types.CallbackQuery):
    await AdminStates.waiting_category_name.set()
    await call.message.edit_text("📂 Yangi kategoriya nomini kiriting:\n(Masalan: Matematika)")

async def adm_cat_name(msg: types.Message, state: FSMContext):
    await state.update_data(cat_name=msg.text)
    await AdminStates.waiting_category_emoji.set()
    await msg.answer("Kategoriya uchun emoji kiriting:\n(Masalan: 📐 yoki 🧪)\nDefault: 📚")

async def adm_cat_emoji(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    emoji = msg.text.strip() if msg.text else "📚"
    await db.add_category(data["cat_name"], emoji)
    await state.finish()
    cats = await db.get_all_categories_admin()
    await msg.answer(f"✅ '{data['cat_name']}' kategoriyasi qo'shildi!", reply_markup=admin_categories_kb(cats))

async def adm_cat_menu_cb(call: types.CallbackQuery):
    cat_id = int(call.data.split("_")[2])
    cat = await db.get_category_by_id(cat_id)
    secs = await db.get_sections_by_category_admin(cat_id)
    await call.message.edit_text(
        f"{cat[2]} <b>{cat[1]}</b>\n\n📋 Bo'limlar: <b>{len(secs)}</b>",
        reply_markup=admin_category_menu_kb(cat_id)
    )

async def adm_del_cat_cb(call: types.CallbackQuery):
    cat_id = int(call.data.split("_")[3])
    await call.message.edit_text("⚠️ Kategoriyani o'chirsangiz barcha ma'lumotlar o'chadi!\n\nTasdiqlaysizmi?", reply_markup=confirm_kb(f"delcat_{cat_id}"))

async def adm_confirm_delcat_cb(call: types.CallbackQuery):
    cat_id = int(call.data.split("_")[2])
    await db.delete_category(cat_id)
    cats = await db.get_all_categories_admin()
    await call.message.edit_text("✅ Kategoriya o'chirildi!", reply_markup=admin_categories_kb(cats))

async def cancel_cb(call: types.CallbackQuery):
    await call.message.delete()
    await call.answer("Bekor qilindi.")

async def adm_sections_cb(call: types.CallbackQuery):
    cat_id = int(call.data.split("_")[2])
    secs = await db.get_sections_by_category_admin(cat_id)
    await call.message.edit_text(f"📝 <b>Bo'limlar</b> ({len(secs)} ta)", reply_markup=admin_sections_kb(secs, cat_id))

async def adm_add_sec_cb(call: types.CallbackQuery, state: FSMContext):
    cat_id = int(call.data.split("_")[3])
    await state.update_data(cat_id=cat_id)
    await AdminStates.waiting_section_name.set()
    await call.message.edit_text("📝 Yangi bo'lim nomini kiriting:\n(Masalan: 1-variant)")

async def adm_sec_name(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    cat_id = data["cat_id"]
    await db.add_section(cat_id, msg.text)
    await state.finish()
    secs = await db.get_sections_by_category_admin(cat_id)
    await msg.answer(f"✅ '{msg.text}' bo'limi qo'shildi!", reply_markup=admin_sections_kb(secs, cat_id))

async def adm_sec_menu_cb(call: types.CallbackQuery):
    sec_id = int(call.data.split("_")[2])
    sec = await db.get_section_by_id(sec_id)
    q_count = await db.get_questions_count(sec_id)
    await call.message.edit_text(
        f"📝 <b>{sec[2]}</b>\n\n❓ Savollar: <b>{q_count}/25</b>",
        reply_markup=admin_section_menu_kb(sec_id, q_count)
    )

async def adm_back_secs_cb(call: types.CallbackQuery):
    sec_id = int(call.data.split("_")[3])
    sec = await db.get_section_by_id(sec_id)
    cat_id = sec[1]
    secs = await db.get_sections_by_category_admin(cat_id)
    await call.message.edit_text(f"📝 <b>Bo'limlar</b> ({len(secs)} ta)", reply_markup=admin_sections_kb(secs, cat_id))

async def adm_del_sec_cb(call: types.CallbackQuery):
    sec_id = int(call.data.split("_")[3])
    await call.message.edit_text("⚠️ Bo'limni o'chirsangiz barcha savollar ham o'chadi!\n\nTasdiqlaysizmi?", reply_markup=confirm_kb(f"delsec_{sec_id}"))

async def adm_confirm_delsec_cb(call: types.CallbackQuery):
    sec_id = int(call.data.split("_")[2])
    await db.delete_section(sec_id)
    await call.message.edit_text("✅ Bo'lim o'chirildi!")

async def adm_questions_cb(call: types.CallbackQuery):
    sec_id = int(call.data.split("_")[2])
    questions = await db.get_questions_by_section(sec_id)
    await call.message.edit_text(f"❓ <b>Savollar</b> ({len(questions)}/25)", reply_markup=admin_questions_kb(questions, sec_id))

async def adm_q_detail_cb(call: types.CallbackQuery):
    q_id = int(call.data.split("_")[2])
    q = await db.get_question_by_id(q_id)
    if not q: await call.answer("Savol topilmadi!", show_alert=True); return
    q_id, sec_id, text, a, b, c, d, correct, _ = q
    await call.message.edit_text(
        f"❓ <b>Savol #{q_id}</b>\n\n{text}\n\n🅰️ {a}\n🅱️ {b}\n🅲 {c}\n🅳 {d}\n\n✅ To'g'ri: <b>{correct}</b>",
        reply_markup=admin_question_menu_kb(q_id, sec_id)
    )

async def adm_add_q_cb(call: types.CallbackQuery, state: FSMContext):
    sec_id = int(call.data.split("_")[3])
    q_count = await db.get_questions_count(sec_id)
    if q_count >= 25: await call.answer("⚠️ Bu bo'limda allaqachon 25 ta savol bor!", show_alert=True); return
    await state.update_data(sec_id=sec_id)
    await AdminStates.waiting_question_text.set()
    await call.message.edit_text(f"❓ Savol matni ({q_count+1}/25):\n\nSavol matnini kiriting:")

async def adm_q_text(msg: types.Message, state: FSMContext):
    await state.update_data(q_text=msg.text)
    await AdminStates.waiting_option_a.set()
    await msg.answer("🅰️ A variantini kiriting:")

async def adm_q_a(msg: types.Message, state: FSMContext):
    await state.update_data(option_a=msg.text)
    await AdminStates.waiting_option_b.set()
    await msg.answer("🅱️ B variantini kiriting:")

async def adm_q_b(msg: types.Message, state: FSMContext):
    await state.update_data(option_b=msg.text)
    await AdminStates.waiting_option_c.set()
    await msg.answer("🅲 C variantini kiriting:")

async def adm_q_c(msg: types.Message, state: FSMContext):
    await state.update_data(option_c=msg.text)
    await AdminStates.waiting_option_d.set()
    await msg.answer("🅳 D variantini kiriting:")

async def adm_q_d(msg: types.Message, state: FSMContext):
    await state.update_data(option_d=msg.text)
    await AdminStates.waiting_correct.set()
    await msg.answer("✅ To'g'ri javobni kiriting:\nFaqat: <b>A</b>, <b>B</b>, <b>C</b> yoki <b>D</b>")

async def adm_q_correct(msg: types.Message, state: FSMContext):
    answer = msg.text.strip().upper()
    if answer not in ["A", "B", "C", "D"]: await msg.answer("❌ Faqat A, B, C yoki D kiriting!"); return
    data = await state.get_data()
    await state.finish()
    await db.add_question(data["sec_id"], data["q_text"], data["option_a"], data["option_b"], data["option_c"], data["option_d"], answer)
    q_count = await db.get_questions_count(data["sec_id"])
    sec = await db.get_section_by_id(data["sec_id"])
    await msg.answer(
        f"✅ Savol qo'shildi!\n\n📝 Bo'lim: <b>{sec[2]}</b>\n❓ Savollar: <b>{q_count}/25</b>",
        reply_markup=admin_section_menu_kb(data["sec_id"], q_count)
    )

async def adm_del_q_cb(call: types.CallbackQuery):
    parts = call.data.split("_")
    q_id = int(parts[3]); sec_id = int(parts[4])
    await call.message.edit_text("⚠️ Bu savolni o'chirishni tasdiqlaysizmi?", reply_markup=confirm_kb(f"delq_{q_id}_{sec_id}"))

async def adm_confirm_delq_cb(call: types.CallbackQuery):
    parts = call.data.split("_")
    q_id = int(parts[2]); sec_id = int(parts[3])
    await db.delete_question(q_id)
    questions = await db.get_questions_by_section(sec_id)
    await call.message.edit_text(f"✅ Savol o'chirildi!\n\n❓ Savollar ({len(questions)}/25):", reply_markup=admin_questions_kb(questions, sec_id))

async def cancel_cmd(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("❌ Bekor qilindi.", reply_markup=admin_main_kb())

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_panel, commands=["admin"], state="*")
    dp.register_message_handler(cancel_cmd, commands=["cancel"], state="*")
    dp.register_message_handler(back_to_user, text="🔙 Foydalanuvchi rejimi", state="*")
    dp.register_message_handler(admin_stats, text="📊 Statistika", state="*")
    dp.register_message_handler(admin_users, text="👤 Foydalanuvchilar", state="*")
    dp.register_message_handler(admin_categories, text="📂 Kategoriyalar", state="*")
    dp.register_message_handler(broadcast_start, text="📨 Xabar yuborish", state="*")
    dp.register_message_handler(broadcast_send, state=AdminStates.waiting_broadcast)
    dp.register_message_handler(adm_cat_name, state=AdminStates.waiting_category_name)
    dp.register_message_handler(adm_cat_emoji, state=AdminStates.waiting_category_emoji)
    dp.register_message_handler(adm_sec_name, state=AdminStates.waiting_section_name)
    dp.register_message_handler(adm_q_text, state=AdminStates.waiting_question_text)
    dp.register_message_handler(adm_q_a, state=AdminStates.waiting_option_a)
    dp.register_message_handler(adm_q_b, state=AdminStates.waiting_option_b)
    dp.register_message_handler(adm_q_c, state=AdminStates.waiting_option_c)
    dp.register_message_handler(adm_q_d, state=AdminStates.waiting_option_d)
    dp.register_message_handler(adm_q_correct, state=AdminStates.waiting_correct)
    dp.register_callback_query_handler(adm_back_cats_cb, text="adm_back_cats", state="*")
    dp.register_callback_query_handler(adm_add_cat_cb, text="adm_add_cat", state="*")
    dp.register_callback_query_handler(adm_cat_menu_cb, lambda c: c.data.startswith("adm_cat_"), state="*")
    dp.register_callback_query_handler(adm_del_cat_cb, lambda c: c.data.startswith("adm_del_cat_"), state="*")
    dp.register_callback_query_handler(adm_confirm_delcat_cb, lambda c: c.data.startswith("confirm_delcat_"), state="*")
    dp.register_callback_query_handler(cancel_cb, text="cancel_action", state="*")
    dp.register_callback_query_handler(adm_sections_cb, lambda c: c.data.startswith("adm_sections_"), state="*")
    dp.register_callback_query_handler(adm_add_sec_cb, lambda c: c.data.startswith("adm_add_sec_"), state="*")
    dp.register_callback_query_handler(adm_sec_menu_cb, lambda c: c.data.startswith("adm_sec_"), state="*")
    dp.register_callback_query_handler(adm_back_secs_cb, lambda c: c.data.startswith("adm_back_secs_"), state="*")
    dp.register_callback_query_handler(adm_del_sec_cb, lambda c: c.data.startswith("adm_del_sec_"), state="*")
    dp.register_callback_query_handler(adm_confirm_delsec_cb, lambda c: c.data.startswith("confirm_delsec_"), state="*")
    dp.register_callback_query_handler(adm_questions_cb, lambda c: c.data.startswith("adm_questions_"), state="*")
    dp.register_callback_query_handler(adm_q_detail_cb, lambda c: c.data.startswith("adm_q_"), state="*")
    dp.register_callback_query_handler(adm_add_q_cb, lambda c: c.data.startswith("adm_add_q_"), state="*")
    dp.register_callback_query_handler(adm_del_q_cb, lambda c: c.data.startswith("adm_del_q_"), state="*")
    dp.register_callback_query_handler(adm_confirm_delq_cb, lambda c: c.data.startswith("confirm_delq_"), state="*")
