from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

def main_menu_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📚 Fanlar"))
    kb.row(KeyboardButton("📊 Natijalarim"), KeyboardButton("ℹ️ Ma'lumot"))
    return kb

def categories_kb(categories):
    kb = InlineKeyboardMarkup()
    for cat in categories:
        cat_id, name, emoji, *_ = cat
        kb.add(InlineKeyboardButton(f"{emoji} {name}", callback_data=f"cat_{cat_id}"))
    kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_main"))
    return kb

def sections_kb(sections, cat_id):
    kb = InlineKeyboardMarkup()
    for sec in sections:
        sec_id, _, name, *_ = sec
        kb.add(InlineKeyboardButton(f"📝 {name}", callback_data=f"sec_{sec_id}"))
    kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_cats"))
    return kb

def start_test_kb(sec_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🚀 Testni boshlash", callback_data=f"start_test_{sec_id}"))
    kb.add(InlineKeyboardButton("🏆 Reyting", callback_data=f"rating_{sec_id}"))
    kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"back_sec_{sec_id}"))
    return kb

def answer_kb(q_index):
    kb = InlineKeyboardMarkup(row_width=4)
    kb.row(
        InlineKeyboardButton("A", callback_data=f"ans_{q_index}_A"),
        InlineKeyboardButton("B", callback_data=f"ans_{q_index}_B"),
        InlineKeyboardButton("C", callback_data=f"ans_{q_index}_C"),
        InlineKeyboardButton("D", callback_data=f"ans_{q_index}_D"),
    )
    kb.add(InlineKeyboardButton("🚫 Testni yakunlash", callback_data="finish_test"))
    return kb

def result_kb(sec_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔄 Qayta urinish", callback_data=f"start_test_{sec_id}"))
    kb.add(InlineKeyboardButton("🏆 Reyting", callback_data=f"rating_{sec_id}"))
    kb.add(InlineKeyboardButton("🔙 Bosh menyu", callback_data="back_main"))
    return kb

def admin_main_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("📂 Kategoriyalar"), KeyboardButton("📊 Statistika"))
    kb.row(KeyboardButton("📨 Xabar yuborish"), KeyboardButton("👤 Foydalanuvchilar"))
    kb.add(KeyboardButton("🔙 Foydalanuvchi rejimi"))
    return kb

def admin_categories_kb(categories):
    kb = InlineKeyboardMarkup()
    for cat in categories:
        cat_id, name, emoji, *_ = cat
        kb.add(InlineKeyboardButton(f"{emoji} {name}", callback_data=f"adm_cat_{cat_id}"))
    kb.add(InlineKeyboardButton("➕ Kategoriya qo'shish", callback_data="adm_add_cat"))
    return kb

def admin_category_menu_kb(cat_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📝 Bo'limlar", callback_data=f"adm_sections_{cat_id}"))
    kb.add(InlineKeyboardButton("🗑 Kategoriyani o'chirish", callback_data=f"adm_del_cat_{cat_id}"))
    kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data="adm_back_cats"))
    return kb

def admin_sections_kb(sections, cat_id):
    kb = InlineKeyboardMarkup()
    for sec in sections:
        sec_id, _, name, *_ = sec
        kb.add(InlineKeyboardButton(f"📝 {name}", callback_data=f"adm_sec_{sec_id}"))
    kb.add(InlineKeyboardButton("➕ Bo'lim qo'shish", callback_data=f"adm_add_sec_{cat_id}"))
    kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"adm_cat_{cat_id}"))
    return kb

def admin_section_menu_kb(sec_id, q_count):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(f"❓ Savollar ({q_count}/25)", callback_data=f"adm_questions_{sec_id}"))
    kb.add(InlineKeyboardButton("➕ Savol qo'shish", callback_data=f"adm_add_q_{sec_id}"))
    kb.add(InlineKeyboardButton("🗑 Bo'limni o'chirish", callback_data=f"adm_del_sec_{sec_id}"))
    kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"adm_back_secs_{sec_id}"))
    return kb

def admin_questions_kb(questions, sec_id):
    kb = InlineKeyboardMarkup()
    for i, q in enumerate(questions):
        q_id = q[0]
        text = q[2][:25] + "..." if len(q[2]) > 25 else q[2]
        kb.add(InlineKeyboardButton(f"{i+1}. {text}", callback_data=f"adm_q_{q_id}"))
    kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"adm_sec_{sec_id}"))
    return kb

def admin_question_menu_kb(q_id, sec_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🗑 Savolni o'chirish", callback_data=f"adm_del_q_{q_id}_{sec_id}"))
    kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"adm_questions_{sec_id}"))
    return kb

def confirm_kb(action):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("✅ Ha", callback_data=f"confirm_{action}"),
        InlineKeyboardButton("❌ Yo'q", callback_data="cancel_action")
    )
    return kb
