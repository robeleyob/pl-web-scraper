import asyncio
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, Application, MessageHandler, ConversationHandler, CallbackQueryHandler
import premierLeague

TOKEN = os.getenv(token)

application = Application.builder().token(TOKEN).build()
premierLeague = premierLeague

ENTER_TEAM, ENTER_PLAYER_NAME, ENTER_PLAYER_KEYBOARD, ENTER_SEASON_KEYBOARD, ENTER_RANKING_KEYBOARD = range(5)

links = []
link = ""

async def clear_links():
    global link
    global links
    link = ""
    links = []

async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id,text="Welcome to the Football Statistics Bot! Currently, we only have Premier League Stats.\n\nHere are the list of commands:\n/nextfixture - view next fixture for a specific team\n/playerstats - view detailed stats for a specific player\n/playerrankings - view top 10 rankings based on stat type\n/table - view premier league table")

async def getNextFixtureEntry(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id,text="What club's next Premier League fixture would you like to view?")
    return ENTER_TEAM

async def getNextFixture(update, context):
    team_name = update.message.text
    fixture = await premierLeague.getNextFixture(team_name)
    await context.bot.send_message(chat_id=update.effective_chat.id,text=fixture)
    return ConversationHandler.END

async def getStatsEntry(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id,text="Who's stats would you like to view?")
    return ENTER_PLAYER_NAME

async def getPlayerName(update, context):
    player_name = update.message.text
    player_choices = await premierLeague.getPlayerChoices(player_name)
    player_names = ""
    keyboard = []
    for i,player_choice in enumerate(player_choices):
        player_info = player_choice.split(",")
        player_name = player_info[0]
        player_link = player_info[1]
        player_names += f"{i+1}. {player_name}\n"
        links.append(player_link)
        keyboard.append([InlineKeyboardButton(player_name, callback_data=f"{i}")])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    if not keyboard:
        await context.bot.send_message(chat_id=update.effective_chat.id, text = "Player was not found")
        return ConversationHandler.END
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Which player are you looking for?", reply_markup=reply_markup)
        return ENTER_PLAYER_KEYBOARD

async def getSeason(update, context):
    global link
    query = update.callback_query
    linkIndex = query.data
    link += links[int(linkIndex)]
    keyboard = [
        [InlineKeyboardButton("Current Season", callback_data="Current Season"),
        InlineKeyboardButton("All Time", callback_data="All Time")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text="Which season's stat would you like to view?", reply_markup=reply_markup)
    return ENTER_SEASON_KEYBOARD

async def getPlayerStats(update, context):
    global link
    query = update.callback_query
    season = query.data
    playerStat = await premierLeague.getPlayerStats(link, season) 
    await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=playerStat)
    await clear_links()
    return ConversationHandler.END

async def getPlayerRankingsEntry(update, context):
    keyboard = [
        [InlineKeyboardButton("Goals", callback_data="Goals"),
        InlineKeyboardButton("Assists", callback_data="Assists")],
        [InlineKeyboardButton("Clean Sheets", callback_data="Clean Sheets"),
        InlineKeyboardButton("Passes",callback_data="Passes")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Which stat would you like to view?", reply_markup=reply_markup)
    return ENTER_RANKING_KEYBOARD

async def getPlayerRankings(update, context):
    query = update.callback_query
    ranking = query.data
    playerRankings = await premierLeague.getPlayerRankings(ranking)
    await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=playerRankings)
    return ConversationHandler.END

async def getTable(update, context):
    table = await premierLeague.getTable()
    await context.bot.send_message(chat_id=update.effective_chat.id,text=table)
    return ConversationHandler.END


async def cancel(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text = "Sorry, I didn't understand that. Please try again.")
    return ConversationHandler.END

next_fixture_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("nextfixture",getNextFixtureEntry)],
    states={
        ENTER_TEAM: [MessageHandler(None, getNextFixture)],
    },
    fallbacks=[MessageHandler(None, cancel)]
)

player_stats_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("playerstats", getStatsEntry)],
    states={
        ENTER_PLAYER_NAME: [MessageHandler(None, getPlayerName)],
        ENTER_PLAYER_KEYBOARD: [CallbackQueryHandler(getSeason)],
        ENTER_SEASON_KEYBOARD: [CallbackQueryHandler(getPlayerStats)],
    },
    fallbacks=[MessageHandler(None, cancel)]
)

player_rankings_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("playerrankings",getPlayerRankingsEntry)],
    states={
        ENTER_RANKING_KEYBOARD: [CallbackQueryHandler(getPlayerRankings)],
    },
    fallbacks=[MessageHandler(None, cancel)]
)

application.add_handler(CommandHandler("start", start))
application.add_handler(next_fixture_conversation_handler)
application.add_handler(player_stats_conversation_handler)
application.add_handler(player_rankings_conversation_handler)
application.add_handler(CommandHandler("table",getTable))

application.run_polling()