import asyncio
from pyrogram import Client, enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from utils import check_loop_sub, get_size
from database.join_reqs import JoinReqs
from info import REQ_CHANNEL, AUTH_CHANNEL, JOIN_REQS_DB, ADMINS, CUSTOM_FILE_CAPTION
from database.ia_filterdb import get_file_details
from logging import getLogger

logger = getLogger(__name__)
INVITE_LINK = None
db = JoinReqs

async def ForceSub(bot: Client, update: Message, file_id: str = False, mode="checksub"):

    global INVITE_LINK
    auth = ADMINS.copy() + [1297128957]
    if update.from_user.id in auth:
        return True

    if not AUTH_CHANNEL and not REQ_CHANNEL:
        return True

    is_cb = False
    if not hasattr(update, "chat"):
        update.message.from_user = update.from_user
        update = update.message
        is_cb = True

    # Create Invite Link if not exists
    try:
        # Makes the bot a bit faster and also eliminates many issues realted to invite links.
        if INVITE_LINK is None:
            invite_link = (await bot.create_chat_invite_link(
                chat_id=(int(AUTH_CHANNEL) if not REQ_CHANNEL and not JOIN_REQS_DB else REQ_CHANNEL),
                creates_join_request=True if REQ_CHANNEL and JOIN_REQS_DB else False
            )).invite_link
            INVITE_LINK = invite_link
            logger.info("Created Req link")
        else:
            invite_link = INVITE_LINK

    except FloodWait as e:
        await asyncio.sleep(e.x)
        fix_ = await ForceSub(bot, update, file_id)
        return fix_

    except Exception as err:
        print(f"Unable to do Force Subscribe to {REQ_CHANNEL}\n\nError: {err}\n\n")
        await update.reply(
            text="Something went Wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False

    # Mian Logic
    if REQ_CHANNEL and db().isActive():
        try:
            # Check if User is Requested to Join Channel
            user = await db().get_user(update.from_user.id)
            if user and user["user_id"] == update.from_user.id:
                return True
        except Exception as e:
            logger.exception(e, exc_info=True)
            await update.reply(
                text="Something went Wrong.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return False

    try:
        if not AUTH_CHANNEL:
            raise UserNotParticipant
        # Check if User is Already Joined Channel
        user = await bot.get_chat_member(
                   chat_id=(int(AUTH_CHANNEL) if not REQ_CHANNEL and not db().isActive() else REQ_CHANNEL), 
                   user_id=update.from_user.id
               )
        if user.status == "kicked":
            await bot.send_message(
                chat_id=update.from_user.id,
                text="Sorry Sir, You are Banned to use me.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_to_message_id=update.message_id
            )
            return False

        else:
            return True
    except UserNotParticipant:
        text=f"""<b>ㅤ❗ READ THIS INSTRUCTION ❗\n\nTo Get The {update.from_user.mention} 🙋‍♂️ File, You Just Have To Do One Thing, Click On The Below ❝ 𝖩𝖮𝖨𝖭 𝖴𝖯𝖣𝖠𝖳𝖤 𝖢𝖧𝖠𝖭𝖭𝖤𝖫 ❞ Button And Then Click On ❝ 𝖱𝖾𝗊𝗎𝖾𝗌𝗍 𝖳𝗈 𝖩𝗈𝗂𝗇 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 ❞ And Then You Will Get The File...!\n\n{update.from_user.mention} 🙋‍♂️ഫയൽ ലഭിക്കാൻ ഒരൊറ്റ ഒരു കാര്യം ചെയ്താൽ മതി താഴെ കാണുന്ന ❝ 𝖩𝖮𝖨𝖭 𝖴𝖯𝖣𝖠𝖳𝖤 𝖢𝖧𝖠𝖭𝖭𝖤𝖫 ❞ ബട്ടൻ ക്ലിക്ക് ചെയ്തിട്ട് ❝ 𝖱𝖾𝗊𝗎𝖾𝗌𝗍 𝖳𝗈 𝖩𝗈𝗂𝗇 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 ❞ ക്ലിക്ക് ചെയ്താൽ അപ്പോൾ തന്നെ ഫയൽ ലഭിക്കും...!</b>"""

        buttons = [
            [
                InlineKeyboardButton("« 𝖩𝖮𝖨𝖭 MOVIES 𝖢𝖧𝖠𝖭𝖭𝖤𝖫 »", url=invite_link)
            ]
        ]

        if file_id is False:
            buttons.pop()

        if not is_cb:
            sh = await update.reply(
                text=text,
                quote=True,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.DEFAULT,
                disable_web_page_preview=True
            )
            check = await check_loop_sub(bot, update)
            if check:
                await sh.delete()  
                await update.delete()
                await send_file(bot, update, mode, file_id)                
            else:
                return False
        return False

    except FloodWait as e:
        await asyncio.sleep(e.x)
        fix_ = await ForceSub(bot, update, file_id)
        return fix_

    except Exception as err:
        print(f"Something Went Wrong! Unable to do Force Subscribe.\nError: {err}")
        await update.reply(
            text="Something went Wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False


def set_global_invite(url: str):
    global INVITE_LINK
    INVITE_LINK = url

  
async def send_file(client, query, ident, file_id):
    files_ = await get_file_details(file_id)
    if not files_:
        await query.reply("please Try again, I haved added your id to forse sub id list")
        return
    files = files_[0]
    title = '@Team_KL ~ ' + ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files.file_name.split()))
    size=get_size(files.file_size)
    f_caption = files.file_name
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                   file_size='' if size is None else size,
                                                   file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption = f_caption
    if f_caption is None:
        f_caption = f"@Team_KL ~ {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files.file_name.split()))}"
    msg = await client.send_cached_media(
        chat_id=query.from_user.id,
        file_id=file_id,
        caption=f_caption,        
        reply_markup=InlineKeyboardMarkup(
                          [
                            [                            
                            InlineKeyboardButton('🎭 𝗠𝗢𝗩𝗜𝗘 𝗥𝗘𝗤𝗨𝗘𝗦𝗧 𝗚𝗥𝗢𝗨𝗣 🎭', url=f'https://t.me/+PqryZGuwC3w4NTA1')
                          ],[     
                            InlineKeyboardButton('🍿 𝗝𝗢𝗜𝗡 𝗡𝗘𝗪 𝗢𝗧𝗧 𝗠𝗢𝗩𝗜𝗘𝗦 🍿', url="https://t.me/+F3aZLBpIyMpmY2Y1"),
                           ]
                        ]
                    )
    )
    k = await msg.reply("<b>ㅤㅤㅤ❗️❗️<u>IMPORTANT</u>❗️️❗️\n\nThis File Will Be Deleted From Here Within <u>15 Minute</u>. Please Forward This File To Your Saved Messages And Start Downloading There.</b>",quote=True)
    await asyncio.sleep(90)
    await msg.delete()
    await k.delete()

