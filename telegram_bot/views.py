from django.shortcuts import render
import telebot

bot = telebot.TeleBot("886807439:AAFXCpSd3YkKdeaJ1a1tgXRCYLrfz0oph4U")


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Hello my friend, you write me "/start"')


bot.polling()
