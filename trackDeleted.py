from scp import user, bot
from scp.utils.cache import Messages  # type: ignore
from typing import List
from scp.utils.parser import getAttr
from scp.utils.MessageTypes import getType, Types  # type: ignore
import asyncio


@user.on_message(
    ~user.filters.me
    & ~user.filters.service,
)
async def _(_, message: user.types.Message):
    Messages.append(message)


SendType = {
    Types.TEXT: bot.send_message,
    Types.STICKER: user.send_sticker,
    Types.DOCUMENT: user.send_document,
    Types.PHOTO: user.send_photo,
    Types.AUDIO: user.send_audio,
    Types.VOICE: user.send_voice,
    Types.VIDEO: user.send_video,
    Types.ANIMATION: user.send_animation,
}


@user.on_deleted_messages(
    ~user.filters.private
    & ~user.filters.me
    & ~user.filters.service,
)
async def _(_, messages: List):
    for mDel in messages:
        for message in Messages:
            if (
                getattr(mDel.chat, 'id', None) == getattr(message.chat, 'id', None)
                and mDel.message_id == message.message_id
            ):
                dataType, content, caption = getType(message)
                text = user.md.KanTeXDocument(
                    user.md.Section(
                        '#DeletedMessage',
                        user.md.SubSection(
                            message.chat.title,
                            user.md.KeyValueItem(
                                user.md.Bold('chat_id'),
                                user.md.Code(
                                    message.chat.id,
                                ),
                            ),
                            user.md.KeyValueItem(
                                user.md.Bold(
                                    'user_id',
                                ),
                                user.md.Code(
                                    getAttr(
                                        message,
                                        ['from_user', 'sender_chat'],
                                    ).id,
                                ),
                            ),
                            user.md.KeyValueItem(
                                user.md.Bold('message_id'),
                                user.md.Code(
                                    message.message_id,
                                ),
                            ),
                            user.md.KeyValueItem(
                                user.md.Bold('content'),
                                user.md.Code(
                                    f'\n{content}',
                                ),
                            ),
                            user.md.KeyValueItem(
                                user.md.Bold('caption(media)'),
                                user.md.Code(
                                    f'\n{caption}',
                                ),
                            ) if message.caption else None,
                        ),
                    ),
                )
                return await dataTypeCheck(
                    dataType,
                    content,
                    text,
                )


async def dataTypeCheck(
    dataType: int,
    content: str,
    text: user.md.KanTeXDocument,
):
    try:
        if dataType == Types.TEXT:
            return await SendType[dataType](
                user.log_channel,
                text,
            )
        elif dataType == Types.STICKER:
            await SendType[dataType](
                user.log_channel,
                content,
            )
            return await SendType[Types.TEXT](
                user.log_channel,
                text,
            )
        else:
            return await SendType[dataType](
                user.log_channel,
                content,
                caption=text,
            )
    except user.exceptions.exceptions.bad_request_400.FileReferenceExpired:
        ...


async def clearMessages(
    seconds=86400  # 1 day
):
    while not await asyncio.sleep(seconds):
        Messages.clear()


asyncio.create_task(clearMessages())
