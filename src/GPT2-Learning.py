#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import json, os, string, sys, threading, random, model, sample, encoder, logging, time
import numpy as np
import tensorflow as tf
import re
import os

# prefixes; change if and when required by your implementation
input_prefix = "|kysymys|"
output_prefix = "|vastaus|"

# Check if the token file exists
if not os.path.isfile('bot_token.txt'):
    print("Error: token.txt file doesn't exist. Please create the file and add your token.")
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
top = 0.77

# Temperature (refer to gpt-2 documentation)
degree = 1.1

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

def runn(bot, update):
    retr = False
    new = retr
    comput = threading.Thread(target=wait, args=(bot, update, new,))
    comput.start()

def wait(bot, update, new):
    global tim
    global user
    global running
    global mode
    global learn
    global learning
    global cache
    if user == "":
        user = update.message.from_user.id
    if user == update.message.from_user.id:
        user = update.message.from_user.id
        temp = timeout
        compute = threading.Thread(target=interact_model, args=(bot, update, new,))
        compute.start()
        if running == False:
            while temp > 1:
                running = True
                time.sleep(1)
                temp = temp - 1
            if running == True:
                mode = False
                learn = False
                learning = ""
                cache = ""
                user = ""
                update.message.reply_text(txt_info_reset_msg)
                running = False
    else:
        left = str(60)
        update.message.reply_text(txt_info_bot_busy + left + ' sekuntia.')

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

def interact_model(bot, update, new):
    model_name = 'fenno'
    seed = random.randint(1431655765, 2863311530)
    nsamples = 1
    batch_size = 1
    top_k = tok
    topp = top
    models_dir = 'models'
    tex = str(update.message.text)
    global learning
    global learn
    global mode
    global cache
    global turns  # Keep track of conversation turns

    enc = encoder.get_encoder(model_name, models_dir)

    if mode == True:
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
        out = sess.run(output, feed_dict={
            context: [context_tokens for _ in range(batch_size)]
        })[:, len(context_tokens):]
        for i in range(batch_size):
            generated += 1
            text = enc.decode(out[i])
            if debug == True:
                print("==========")
                print("Raw output: " + text)
                print("==========")

            splitted = text.splitlines()[0]
            turns.append(splitted + '\n')  # Append the bot's response to the turns list
            encodedstr = splitted.encode(encoding=sys.stdout.encoding,errors='ignore')
            decodedstr = encodedstr.decode("utf-8")
            final = str(decodedstr)
            sanitized = regex(final)
            finalsan = final
            if learn == True:
                learning = raw_text + finalsan + " "
            update.message.reply_text(finalsan)
            if debug == True:
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

def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    # update; use in TG api v12 => updater = Updater('TOKEN', use_context=True)
    updater = Updater(bot_token, use_context=False)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # on different commands - answer in Telegram

# alkuperäiset komennot // original commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("chatbot", chatbot))
    dp.add_handler(CommandHandler("finish", finish))
    dp.add_handler(CommandHandler("learnon", learnon))  
    dp.add_handler(CommandHandler("learnoff", learnoff))    
    dp.add_handler(CommandHandler("learnreset", learnreset))
    dp.add_handler(CommandHandler("reset", learnreset))    
    dp.add_handler(CommandHandler("retry", retry))

# suomi-komennot /// Finnish commands
    dp.add_handler(CommandHandler("aloita", start))    
    dp.add_handler(CommandHandler("apua", help))
    dp.add_handler(CommandHandler("lopeta", finish))
    dp.add_handler(CommandHandler("opi", learnon))  
    dp.add_handler(CommandHandler("eioppia", learnoff))    
    dp.add_handler(CommandHandler("nollaa", learnreset))
    dp.add_handler(CommandHandler("uusiks", retry))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, runn))
    # log all errors
    dp.add_error_handler(error)
    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
