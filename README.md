## About this fork

This is a fork from the original GPT-2 Telegram Chatbot from xwarfare (https://github.com/xwarfare/GPT2-Telegram-Chatbot). It's been modified to suit a Finnish GPT-2 model and uses updated code for the Telegram API handling and so forth. 

Put your API token in the `src` directory under `token.txt`.
You will also likely need to customize the chat prefix, the chat suffix and other elements of the chat handling yourself.

Currently, this runs on a newer `python-telegram-bot` version (v20.7) + you can use the latest TensorFlow 2.x instead of TF1 for this.

## Changelog
- v0.033 - 17 Jan 2024 - the rest of the command handlers fixed
- v0.032 - 17 Jan 2024 - `async` fixes
- v0.03 - 10 Jan 2024 - **the bot now uses `telegram-python-bot` library v20.7**
  - updated the bot to use the latest `telegram-python-bot` features and made it more asynchronous
- v0.02 - 23 July 2023 - **starting context, `/temp` temperature setting**
  - You can now write a starting context for the model for better dialogue priming, see the variable: `starting_context`.
  - model temperature can now be user-set with `/temp <temp>`, i.e. `/temp 0.9` for a temperature of 0.9
- v0.01 - 1 July 2023 - **Context memory trimmer "fixed"**
-- **the yay's**
  - Finally redid the context memory auto trimmer for seamless sessions without the need for manual resets.
  - Every now and then, the user might still need manual reset with `/reset` if and when things go out of bounds

**the meh's**
- you can only have one user session at a time; hence the time limit per session
- occasionally gets stuck when context memory is overloaded => when trimming context memory (**this needs to be reworked!**)

Overall, this is mainly suitable for testbed purposes and not for production use, so to speak. Then again, when running just right, you can use it to audit your local model (i.e. during model training).

Megathanks to ChaosWhisperer for code help on the memory trimming functionality and for a lot of other stuff.

---
_(original README.md below)_
---

## GPT2-Telegram-Chatbot

A GPT-2 Telegram chatbot that's been relatively tuned for chatting. Feel free to make me PRs and I'll check out your code! The bot isn't 100% accurate all the time (why I coded in a /retry function.)

Since the bot consumes so much memory, I have it programmed in a round-robin sort of mode. Each input will reset a timer on your account ID, once the timer runs down the bot is free for other users to use. You will be notified when the timer runs down, and other users can see how much time is left and if the bot is in use.

### Installation/How to use:

Brief install instructions on Ubuntu 20/WSL.

I highly reccomend looking at the jupyter notebook/ipynb on google collab instead.

Install python3.7 (I think 3.6 might work as well, but not 3.8):

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.7
```

Install pip on python 3.7:

```
wget https://bootstrap.pypa.io/get-pip.py
python3.7 get-pip.py
```

Install requirements inside of bot folder after cloning repository:
```
python3.7 -m pip install -r requirements.txt
```

Note: You realistically need 16GB of ram or a 8GB video card. Otherwise you will wait forever.
You can use GPU functions with atleast a 8GB video card that supports cuda tooklit 10.0 and cudnn for cuda toolkit 10. This install also works on windows with python 3.7 and nvidia, you must run command prompt as admin running python 3.7 on windows.

Download the model:
```
python3.7 download_model.py 1558M
```

Set your telegram bot API key in src/GPT2-Learning.py
```
Replace "BOTKEY" with telegram bot token i.e. "1827396499:AAHifc06oS31oQ9L3TuCiZxD9EIfKPi0oWQ"
```

Run the bot:

If using python3 command:
```
./start.sh
```

If using python3.7 command:
```
python3.7 src/GPT2-Learning.py
```

You can edit start.sh to match your python command as you wish.

### For quick command reference:

```
start - Basic start command.
help - Show quick help command.
chatbot - Chatbot mode, me+you string edit and open-ended questions.
finish - Default finish sentence command counting words as output length.
learnon - Turn on sentence compilation with Me+you string for conversation.
learnoff - Turn off the sentence compilation.
learnreset - Reset the learned conversation.
retry - Retry the current computation.
```
Here's a sample in learning chatbot mode with the latest gpt-2 database and top_p set to 0.83:

```
Me: Hello! How are you today? Are you feeling alright? I hope you are doing well and not getting into any trouble. 
Bot: Yeah, I'm fine. Do you want to make something to eat? 
Me: I already made some food, but thanks! I had some jalapeno poppers. I made a ton of them last night after I sold a lawnmower to some folks I got for free earlier in the day. So what are your plans for the day? 
Bot: Nothing special. Nothing exciting in particular. I just wanna chill out for a bit.  
Me: Just a typical day of kicking back and relaxing huh? Are you gonna watch cartoons or any movies in particular? 
Bot: If it's not sports I'll probably just watch something on the TV.  
Me: Sounds alright. I coded on my chatbot project most of the morning. Was waiting on someone to come buy a projector but they haven't shown up yet unfortunately. What do you do for work if you don't mind me asking? 
Bot: I'm a web developer and engineer. It's fun.   
Me: Cool! I'm also a coder and an ethical hacker. I mostly know how to code in Python but I've been unemployed for some time now after my spine injury. I wish I could have joined the military when I was younger. Were you ever in the military? 
Bot: No. I'm not really too proud of my military career. It ended up taking a huge toll on my back.   
Me: What happened to your back if you don't mind me asking?
Bot: First of all, it's better than before. 
Me: Well that's good to hear. Did you injure your back in the military or doing something else? 
Bot: Nope. It's an old injury. 
Me: Ah I see- Well I'll talk to you later. Sorry about your back! I hope we can catch up tomorrow! 
Bot: Yes, of course. Thanks again for chatting!
```

### Example of learning mode backend:
```
INFO:tensorflow:Restoring parameters from models/1558M/model.ckpt
2020-05-10 14:19:43,794 - tensorflow - INFO - Restoring parameters from models/1558M/model.ckpt
==========
Before splitlines:  Nothing special. Nothing exciting in particular. I just wanna chill out for a bit. You: I'll try to keep my spirits up. Just keep in mind that today's the 10th anniversary of the citywide strike
==========
==========
Mode: True
Learn: True
Length: 44
==========
Before regex:  Nothing special. Nothing exciting in particular. I just wanna chill out for a bit. You: I'll try to keep my spirits up. Just keep in mind that today's the 10th anniversary of the citywide strike
==========
Output:  Nothing special. Nothing exciting in particular. I just wanna chill out for a bit.
==========
Raw_text or Original: You: Hello! How are you today? Are you feeling alright? I hope you are doing well and not getting into any trouble. Me: Yeah, I'm fine. Do you want to make something to eat? You: I already made some food, but thanks! I had some jalapeno poppers. I made a ton of them last night after I sold a lawnmower to some folks I got for free earlier in the day. So what are your plans for the day? Me:
==========
Learning text or Next: You: Hello! How are you today? Are you feeling alright? I hope you are doing well and not getting into any trouble. Me: Yeah, I'm fine. Do you want to make something to eat? You: I already made some food, but thanks! I had some jalapeno poppers. I made a ton of them last night after I sold a lawnmower to some folks I got for free earlier in the day. So what are your plans for the day? Me: Nothing special. Nothing exciting in particular. I just wanna chill out for a bit.
==========
top_p out: 0.8338636363636364
==========
top_p in: 0.83
==========
```

For a list of grammarly scores please see [/SCORES.MD](/SCORES.md).

Tip: 

0.77 top_p can sound emotional, confused and copycat-ish.

0.66 top_p can sound thought-out and literal but can have ascii and cut-off errors.
