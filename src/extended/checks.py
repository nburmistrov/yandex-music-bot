from discord.ext.commands import check, check_any

from .errors import CheckAllFailure, MissingInChannel, \
    ExistingInAnotherChannel, SameChannelsError


def check_all(*checks):
    unwrapped = []
    for wrapped in checks:
        try:
            pred = wrapped.predicate
        except AttributeError:
            raise TypeError(
                '%r must be wrapped by commands.check decorator' % wrapped) from None
        else:
            unwrapped.append(pred)

    async def predicate(ctx):
        for func in unwrapped:
            if not await func(ctx):
                raise CheckAllFailure(
                    f'The check function {func.__name__} failed.')
        # if we're here, all checks passed
        return True
    return check(predicate)


def author_in_any_channel():
    async def predicate(ctx):
        if ctx.author.voice is None:
            raise MissingInChannel('You have to be in the voice channel')

        return True
    return check(predicate)


def bot_in_any_channel():
    async def predicate(ctx):
        if ctx.me.voice is None:
            raise MissingInChannel(
                f'Bot is not in any voice channel, use "{ctx.bot.command_prefix}join"')

        return True
    return check(predicate)


def bot_in_another_channel():
    async def predicate(ctx):
        if ctx.me.voice and ctx.me.voice.channel != ctx.author.voice.channel:
            raise ExistingInAnotherChannel(
                'Bot already in a voice channel, join the same voice channel and use '
                f'"{ctx.bot.command_prefix}leave"')

        return True
    return check(predicate)


def in_same_channel():
    async def predicate(ctx):
        if ctx.me.voice.channel != ctx.author.voice.channel:
            raise SameChannelsError('You have to be in the same voice channel')

        return True
    return check(predicate)
