from scp import user


__PLUGIN__ = 'UrbanDict'
__DOC__ = str(
    user.md.KanTeXDocument(
        user.md.Section(
            'UrbanDictionary Definitions',
            user.md.SubSection(
                'Urban',
                user.md.Code('(*prefix)ud {query}'),
            ),
        ),
    ),
)


def replace_text(text: str):
    return text.replace(
        '"', '',
    ).replace(
        '\\r', '',
    ).replace(
        '\\n', '',
    ).replace(
        '\\', '',
    )


@user.on_message(user.filters.sudo & user.filters.command('ud'))
async def _(_, message: user.types.Message):
    if len(message.text.split()) == 1:
        return await message.delete()
    text = message.text.split(None, 1)[1]
    request = await user.aioclient.get(
        f'http://api.urbandictionary.com/v0/define?term={text}',
    )
    response = await request.json()
    text = user.md.KanTeXDocument(
        user.md.Section(
            'UrbanDictionary',
            user.md.SubSection(
                'Text:',
                user.md.Italic(replace_text(response['list'][0]['word'])),
            ),
            user.md.SubSection(
                'Meaning:',
                user.md.Italic(
                    replace_text(
                        response['list'][0]['definition'],
                    ),
                ),
            ),
            user.md.SubSection(
                'Example:',
                user.md.Italic(replace_text(response['list'][0]['example'])),
            ),
        ),
    )
    await message.reply(text, quote=True)
