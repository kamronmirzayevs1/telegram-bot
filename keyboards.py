from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# ===================== USER KEYBOARDS =====================

def main_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📚 Fanlar"))
    builder.row(KeyboardButton(text="📊 Natijalarim"), KeyboardButton(text="ℹ️ Ma'lumot"))
    return builder.as_markup(resize_keyboard=True)

def categories_kb(categories: list):
    builder = InlineKeyboardBuilder()
    for cat in categories:
        cat_id, name, emoji, *_ = cat
        builder.row(InlineKeyboardButton(
            text=f"{emoji} {name}",
            callback_data=f"cat_{cat_id}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main"))
    return builder.as_markup()

def sections_kb(sections: list, cat_id: int):
    builder = InlineKeyboardBuilder()
    for sec in sections:
        sec_id, _, name, *_ = sec
        builder.row(InlineKeyboardButton(
            text=f"📝 {name}",
            callback_data=f"sec_{sec_id}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_cats"))
    return builder.as_markup()

def start_test_kb(sec_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🚀 Testni boshlash", callback_data=f"start_test_{sec_id}"))
    builder.row(InlineKeyboardButton(text="🏆 Reyting", callback_data=f"rating_{sec_id}"))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"back_sec_{sec_id}"))
    return builder.as_markup()

def answer_kb(q_index: int):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="A", callback_data=f"ans_{q_index}_A"),
        InlineKeyboardButton(text="B", callback_data=f"ans_{q_index}_B"),
        InlineKeyboardButton(text="C", callback_data=f"ans_{q_index}_C"),
        InlineKeyboardButton(text="D", callback_data=f"ans_{q_index}_D"),
    )
    builder.row(InlineKeyboardButton(text="🚫 Testni yakunlash", callback_data=f"finish_test"))
    return builder.as_markup()

def result_kb(sec_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔄 Qayta urinish", callback_data=f"start_test_{sec_id}"))
    builder.row(InlineKeyboardButton(text="🏆 Reyting", callback_data=f"rating_{sec_id}"))
    builder.row(InlineKeyboardButton(text="🔙 Bosh menyu", callback_data="back_main"))
    return builder.as_markup()

# ===================== ADMIN KEYBOARDS =====================

def admin_main_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📂 Kategoriyalar"), KeyboardButton(text="📊 Statistika"))
    builder.row(KeyboardButton(text="📨 Xabar yuborish"), KeyboardButton(text="👤 Foydalanuvchilar"))
    builder.row(KeyboardButton(text="🔙 Foydalanuvchi rejimi"))
    return builder.as_markup(resize_keyboard=True)

def admin_categories_kb(categories: list):
    builder = InlineKeyboardBuilder()
    for cat in categories:
        cat_id, name, emoji, *_ = cat
        builder.row(InlineKeyboardButton(
            text=f"{emoji} {name}",
            callback_data=f"adm_cat_{cat_id}"
        ))
    builder.row(InlineKeyboardButton(text="➕ Kategoriya qo'shish", callback_data="adm_add_cat"))
    return builder.as_markup()

def admin_category_menu_kb(cat_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📝 Bo'limlar", callback_data=f"adm_sections_{cat_id}"))
    builder.row(InlineKeyboardButton(text="🗑 Kategoriyani o'chirish", callback_data=f"adm_del_cat_{cat_id}"))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_back_cats"))
    return builder.as_markup()

def admin_sections_kb(sections: list, cat_id: int):
    builder = InlineKeyboardBuilder()
    for sec in sections:
        sec_id, _, name, *_ = sec
        builder.row(InlineKeyboardButton(
            text=f"📝 {name}",
            callback_data=f"adm_sec_{sec_id}"
        ))
    builder.row(InlineKeyboardButton(text="➕ Bo'lim qo'shish", callback_data=f"adm_add_sec_{cat_id}"))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"adm_cat_{cat_id}"))
    return builder.as_markup()

def admin_section_menu_kb(sec_id: int, q_count: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=f"❓ Savollar ({q_count}/25)",
        callback_data=f"adm_questions_{sec_id}"
    ))
    builder.row(InlineKeyboardButton(text="➕ Savol qo'shish", callback_data=f"adm_add_q_{sec_id}"))
    builder.row(InlineKeyboardButton(text="🗑 Bo'limni o'chirish", callback_data=f"adm_del_sec_{sec_id}"))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"adm_back_secs_{sec_id}"))
    return builder.as_markup()

def admin_questions_kb(questions: list, sec_id: int):
    builder = InlineKeyboardBuilder()
    for i, q in enumerate(questions):
        q_id = q[0]
        text = q[2][:25] + "..." if len(q[2]) > 25 else q[2]
        builder.row(InlineKeyboardButton(
            text=f"{i+1}. {text}",
            callback_data=f"adm_q_{q_id}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"adm_sec_{sec_id}"))
    return builder.as_markup()

def admin_question_menu_kb(q_id: int, sec_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🗑 Savolni o'chirish", callback_data=f"adm_del_q_{q_id}_{sec_id}"))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"adm_questions_{sec_id}"))
    return builder.as_markup()

def confirm_kb(action: str):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Ha", callback_data=f"confirm_{action}"),
        InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel_action")
    )
    return builder.as_markup()
