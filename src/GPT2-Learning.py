#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# fork by FlyingFathead w/ ChaosWhisperer
# forked from: xwarfare/GPT2-Telegram-Chatbot/
# this fork: https://github.com/FlyingFathead/GPT2-Telegram-Chatbot
# this fork's version: v0.03 // Jan 10, 2023
#
# (uses `telegram-python-bot` version 20.7)

from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler
from telegram.ext.filters import TEXT
import asyncio
from asyncio import Queue

# others
import json, os, string, sys, threading, random, model, sample, encoder, logging, time
import numpy as np
import tensorflow as tf
import re
import os
import random

# (for multi-user mode) Initialize an empty dictionary for each user's context
user_contexts = {}
user_temperatures = {}

# >> examp. prefixes; change if and when required by your implementation
# input_prefix = "|kysymys|"
# output_prefix = "|vastaus|"

# >> reverse
# output_prefix = "|kysymys|"
# input_prefix = "|vastaus|"

input_prefix = "|k| "
output_prefix = "|v| "

# >> reverse
# input_prefix = "|v| "
# output_prefix = "|k| "

# Starting context; to prime the model better for dialogue
starting_context = "<|dialogi|>\n"

# Check if the token file exists
if not os.path.isfile('bot_token.txt'):
    print("Error: bot_token.txt file doesn't exist. Please create the file and add your token.")
    exit()

# Read the bot_token from the file
with open('bot_token.txt', 'r') as file:
    bot_token = file.read().strip()

# Enable console logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Console output debug prints
debug = True

# Session timeout in seconds
timeout = 3600

# top_p (refer to gpt-2 documentation)
# top = 0.77
top = 0.77

# Temperature (refer to gpt-2 documentation)
degree = 1.0

# Top_p multiplier - add to top_p per word 
# 0.00375 - may be shorter
# 0.00400
# 0.00425
# 0.00450
# 0.00475
# 0.00500 - may be longer
mx = 0.00500

# Top_K unused here, might be useful eventually.
tok = 0

# This is the start of the learning cache, could be useful eventually.
learning = ""

# End settings
mode = True
learn = True
user = ""
cache = ""
running = False
temps = str(degree)
tpstring = str(top)

# turns
global turns
turns = []

# min and max number of answers (for multi-answer rng)
min_num_answers = 1
max_num_answers = 1

# tekstit
txt_settings_prefix = "[Asetukset/logiikka: "
# 'Just type a message... It could be lagged out. /chatbot goes into Me: You: mode. /finish just finishes the text /learnon for conversation learning mode.'
txt_info_1 = "Kirjoita viestisi."
txt_info_bot_busy = "Botti on tällä hetkellä työn touhussa! Tässä pitää vielä odotella..! "
txt_info_timer_out = "Laskuri on mennyt nollaan. Botti on käynnistetty uudelleen."
txt_info_mode_one = ' GPT-XYZ] Olen nyt oppivassa tsättitilassa. Kirjoita (tai klikkaa) /reset nollataksesi botin! Botti tarvitsee resetin n.2 min välein.\n\nPuhu minulle!'
txt_info_mode_two = ' GPT-XYZ] Olen nyt ei-oppivassa tsättibottitilassa.\n\nPuhu mulle...'
txt_info_mode_three = 'Olen nyt lauseentäydennystilassa.\n\nPuhu mulle...'
txt_info_temp = " lämpötila: "
txt_info_secs_remaining = " sekuntia jäljellä..."
txt_info_reset_msg = 'Aikalaskuri on nollassa. Jos haluat aloittaa uuden istunnon, kirjoita tai klikkaa: /reset'

temp = ""
# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

# updates in telegram's python bot library v.20 =>
bot = Bot(token=bot_token)
update_queue = Queue()

# Define the /roleswap command handler
def roleswap(bot, update):
    
    # Swap input_prefix and output_prefix.
    global input_prefix
    global output_prefix

    # Swap the values of input_prefix and output_prefix
    input_prefix, output_prefix = output_prefix, input_prefix

    # Inform the user about the successful swap
    update.message.reply_text("Roles swapped successfully!")

def start(bot, update):
    """Send a message when the command /start is issued."""
    global running
    global mode
    global learn
    global user
    global tim
    global learning
    global cache
    if user == "":
        user = update.message.from_user.id
        mode = True
        learn = True
        learning = ""
        cache = ""
        if mode == True and learn == True:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_one)
        if mode == True and learn == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_two)
        if mode == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_three)
        return
    if user == update.message.from_user.id:
        mode = True
        learn = True
        learning = ""
        cache = ""
        if mode == True and learn == True:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_one)
        if mode == True and learn == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_two)
        if mode == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_three)
        return
    else:
        left = str(timeout)
        update.message.reply_text(txt_info_bot_busy + left + txt_info_secs_remaining)

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Kirjoita vaan viestis. /reset tyhjentää koko höskän.')

def chatbot(bot, update):
    """Send a message when the command /chatbot is issued."""
    global running
    global mode
    global learn
    global user
    global tim
    global learning
    global cache
    if user == "":
        user = update.message.from_user.id
        mode = True
        learn = False
        learning = ""
        cache = ""
        if mode == True and learn == True:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_one)
        if mode == True and learn == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_two)
        if mode == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_three)
        return
    if user == update.message.from_user.id:
        mode = True
        learn = False
        learning = ""
        cache = ""
        if mode == True and learn == True:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_one)
        if mode == True and learn == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_two)
        if mode == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_three)
        return
    else:
        left = str(timeout)
        update.message.reply_text(txt_info_bot_busy + left + txt_info_secs_remaining)

def finish(bot, update):
    """Send a message when the command /finish is issued."""
    global running
    global mode
    global learn
    global user
    global tim
    global learning
    global cache
    if user == "":
        user = update.message.from_user.id
        mode = False
        learn = False
        learning = ""
        cache = ""
        if mode == True and learn == True:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_one)
        if mode == True and learn == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_two)
        if mode == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_three)
        return
    if user == update.message.from_user.id:
        mode = False
        learn = False
        learning = ""
        cache = ""
        if mode == True and learn == True:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_one)
        if mode == True and learn == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_two)
        if mode == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_three)
        return
    else:
        left = str(timeout)
        update.message.reply_text(txt_info_bot_busy + left + txt_info_secs_remaining)

def learnon(bot, update):
    """Send a message when the command /learnon is issued."""
    global running
    global mode
    global learn
    global user
    global tim
    global learning
    global cache
    if user == "":
        user = update.message.from_user.id
        mode = True
        learn = True
        learning = ""
        cache = ""
        if mode == True and learn == True:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_one)
        if mode == True and learn == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_two)
        if mode == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_three)
        return
    if user == update.message.from_user.id:
        mode = True
        learn = True
        learning = ""
        cache = ""
        if mode == True and learn == True:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_one)
        if mode == True and learn == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_two)
        if mode == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_three)
        return
    else:
        left = str(timeout)
        update.message.reply_text(txt_info_bot_busy + left + txt_info_secs_remaining)

def learnoff(bot, update):
    """Send a message when the command /learnoff is issued."""
    global running
    global mode
    global learn
    global user
    global tim
    global learning
    global cache
    if user == "":
        user = update.message.from_user.id
        mode = True
        learn = False
        learning = ""
        cache = ""
        if mode == True and learn == True:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_one)
        if mode == True and learn == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_two)
        if mode == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_three)
        return
    if user == update.message.from_user.id:
        mode = True
        learn = False
        learning = ""
        cache = ""
        if mode == True and learn == True:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_one)
        if mode == True and learn == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_two)
        if mode == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_three)
        return
    else:
        left = str(timeout)
        update.message.reply_text(txt_info_bot_busy + left + txt_info_secs_remaining)

def learnreset(bot, update):
    """Send a message when the command /learnreset is issued."""
        
    global running
    global mode
    global learn
    global user
    global tim
    global learning
    global cache
    global turns  # Add this line to access the global turns list

    turns = []  # Clear the turns list
    learning = ""
    cache = ""

    if user == "":
        user = update.message.from_user.id
    if user == update.message.from_user.id:
        user = update.message.from_user.id
        turns = []  # Clear the turns list
        mode = True
        learn = True
        learning = ""
        cache = ""
        if mode == True and learn == True:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_one)
        if mode == True and learn == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_two)
        if mode == False:
            update.message.reply_text(txt_settings_prefix + tpstring + txt_info_temp + temps + txt_info_mode_three)
        return
    else:
        left = str(timeout)
        update.message.reply_text(txt_info_bot_busy + left + txt_info_secs_remaining)
        running = False  # Add this line to set running to False after the timeout

def regex(mew):
    meow = mew
    if output_prefix in meow:
        meow = meow[0:meow.find(output_prefix)]
        if input_prefix in meow:
            meow = meow[0:meow.find(input_prefix)]
        return meow
    if input_prefix in meow:
        meow = meow[0:meow.find(input_prefix)]
        if output_prefix in meow:
            meow = meow[0:meow.find(output_prefix)]
        return meow
    if "?" in meow:
        meow = meow[0:meow.find('?')]
        meow = meow + "?"
        return meow
    if "!" in meow:
        meow = meow.rsplit('!', 1)[0]
        meow = meow + "!"
        return meow
    else:
        meow = meow.rsplit('.', 1)[0]
        meow = meow + "."
        return meow
    meow = "Nyt tapahtui joku virhe."
    return meow

def retry(bot, update):
    retr = True
    new = retr
    comput = threading.Thread(target=wait, args=(bot, update, new,))
    comput.start()

def runn(update, context):
    user_id = update.effective_user.id
    message_text = update.message.text
    retr = False
    new = retr
    # Schedule the wait coroutine as a task in the asyncio event loop
    asyncio.create_task(wait(context.bot, user_id, message_text, new))

async def wait(bot, user_id, message_text, new):
    global tim
    global user
    global running
    global mode
    global learn
    global learning
    global cache
    global turns

    # Call the asynchronous interact_model function with await
    await interact_model(bot, user_id, message_text, new)

    if user == "":
        user = user_id
    if user == user_id:
        user = user_id
        temp = timeout
        if not running:
            while temp > 0:
                running = True
                await asyncio.sleep(1)  # Use asyncio.sleep instead of time.sleep
                temp -= 1
            if running:
                mode = False
                learn = False
                learning = ""
                cache = ""
                user = ""
                # Send an asynchronous message with await
                await bot.send_message(chat_id=user_id, text=txt_info_reset_msg)
                running = False
    else:
        left = str(timeout - temp)
        # Send an asynchronous message with await
        await bot.send_message(chat_id=user_id, text=txt_info_bot_busy + left + ' sekuntia.')

    # Set running to False after the timeout
    running = False

# helper to fit to 1024 token size
def reduce_to_fit(tokens, max_tokens, enc):
    if len(tokens) <= max_tokens:
        return tokens

    while len(tokens) > max_tokens:
        try:
            second_question_index = tokens.index(enc.encode(input_prefix)[0], len(enc.encode(input_prefix)))
        except ValueError:
            print("Cannot reduce the text further!")
            break
        tokens = tokens[second_question_index:]
    return tokens

async def interact_model(bot, user_id, message_text, new):
    # model details
    model_name = 'fenno'
    seed = random.randint(1431655765, 2863311530)
    nsamples = 1
    batch_size = 1
    top_k = tok
    topp = top
    models_dir = 'models'
    # tex = str(update.message.text)
    # Use message_text instead of update.message.text    
    tex = str(message_text)

    global learning
    global learn
    global mode
    global cache
    global turns  # Keep track of conversation turns

    # Add the starting context
    if new:  # If this is a new conversation, reset the list of turns
        turns = [starting_context]

    num_answers = random.randint(min_num_answers, max_num_answers)  # Randomize the number of answers

    enc = encoder.get_encoder(model_name, models_dir)

    if mode:
        if new:  # If this is a new conversation, reset the list of turns
            turns = []

        # Check total token count of the history plus the new user input
        potential_context = ''.join(turns) + input_prefix + tex + '\n' + output_prefix
        total_tokens = len(enc.encode(potential_context))

        # If too many tokens, remove turns from the start
        while total_tokens > 800:
            if len(turns) == 1:
                print("Cannot reduce the text further!")
                return
            turns.pop(0)
            potential_context = ''.join(turns) + input_prefix + tex + '\n' + output_prefix
            total_tokens = len(enc.encode(potential_context))

        # Add the user's input to the context after it's guaranteed to fit
        turns.append(input_prefix + tex + '\n' + output_prefix)

        raw_text = potential_context
        context_tokens = enc.encode(raw_text)
        length = 300  # Set the default length

    toppf = float(topp)
    lengthm = float(len(enc.encode(raw_text)))
    multf = float(mx)
    lxm = float(lengthm * multf)
    top_p = lxm + toppf

    # The max here is 0.84 and minimum 0.005
    if top_p > 0.84:
        top_p = 0.84
    if top_p < 0.010:
        top_p = 0.010

    models_dir = os.path.expanduser(os.path.expandvars(models_dir))
    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0
    hparams = model.default_hparams()
    with open(os.path.join(models_dir, model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))
    if length is None:
        length = hparams.n_ctx // 2
    elif length > hparams.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.compat.v1.Session(graph=tf.Graph()) as sess:
        context = tf.compat.v1.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.compat.v1.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=degree, top_k=top_k, top_p=top_p
        )

        saver = tf.compat.v1.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join(models_dir, model_name))
        saver.restore(sess, ckpt)

        generated = 0
        while generated < num_answers:
            out = sess.run(output, feed_dict={
                context: [context_tokens for _ in range(batch_size)]
            })[:, len(context_tokens):]
            
            for i in range(batch_size):
                generated += 1
                text = enc.decode(out[i])
                # Split the generated text on newline characters and only keep the first part
                text = text.split('\n')[0]
                # Rest of the code                
                if debug:
                    print("==========")
                    print("Raw output: " + text)
                    print("==========")

                splitted = text.splitlines()[0]
                turns.append(splitted + '\n')  # Append the bot's response to the turns list
                encodedstr = splitted.encode(encoding=sys.stdout.encoding, errors='ignore')
                decodedstr = encodedstr.decode("utf-8")
                final = str(decodedstr)
                sanitized = regex(final)
                finalsan = final
                if learn:
                    learning = raw_text + finalsan + " "
                await bot.send_message(chat_id=user_id, text=finalsan)
                if debug:
                    modes = str(mode)
                    print("Chatbot mode: " + modes)
                    learns = str(learn)
                    print("Learning mode: " + learns)
                    lengths = str(length)
                    print("Length: " + lengths)
                    print("==========")
                    splits = str(splitted)
                    print("Before regex: " + splits)
                    print("==========")
                    print("Output: " + finalsan)
                    print("==========")
                    print("Raw_text or Original: " + raw_text)
                    print("==========")
                    print("Learning text or Next: " + learning)
                    print("==========")
                    tps = str(top_p)
                    print("Final top_p: " + tps)
                    print("==========")
                    print("top_p in: " + tpstring)
                    print("==========")

    sess.close()

# set temperature via msg
def set_temperature(update, context):
    global temperature
    try:
        # args[0] should contain the new temperature as a string
        new_temp = float(args[0])
        if 0 <= new_temp <= 1.1:
            temperature = new_temp
            update.message.reply_text("Lämpötila on nyt: " + str(temperature))
        else:
            update.message.reply_text("Invalid temperature. Please provide a value between 0 and 1.1.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /temp <value>")

# Error logging
def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Start the bot
def main():
    # Ensure that bot_token is available
    if not os.path.isfile('bot_token.txt'):
        print("Error: bot_token.txt file doesn't exist. Please create the file and add your token.")
        exit()

    with open('bot_token.txt', 'r') as file:
        bot_token = file.read().strip()

    # Initialize logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Create an Application instance
    application = Application.builder().token(bot_token).build()

    # alkuperäiset komennot // original commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("chatbot", chatbot))
    application.add_handler(CommandHandler("finish", finish))
    application.add_handler(CommandHandler("learnon", learnon))  
    application.add_handler(CommandHandler("learnoff", learnoff))    
    application.add_handler(CommandHandler("learnreset", learnreset))
    application.add_handler(CommandHandler("reset", learnreset))    
    application.add_handler(CommandHandler("retry", retry))
    application.add_handler(CommandHandler("roleswap", roleswap))

    # suomi-komennot /// Finnish commands
    application.add_handler(CommandHandler("aloita", start))    
    application.add_handler(CommandHandler("apua", help))
    application.add_handler(CommandHandler("lopeta", finish))
    application.add_handler(CommandHandler("opi", learnon))  
    application.add_handler(CommandHandler("eioppia", learnoff))    
    application.add_handler(CommandHandler("nollaa", learnreset))
    application.add_handler(CommandHandler("uusiks", retry))
    application.add_handler(CommandHandler("rooli", roleswap))

    # set the temperature
    application.add_handler(CommandHandler("temp", set_temperature))

    # on noncommand i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(TEXT, runn))

    # log all errors
    application.add_error_handler(error)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
