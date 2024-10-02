# capture audio with microphone
# process audio [...]
# convert audio to text

# capture audio with microphone

# 

from modules.sqlqueue import SqlQueue


voicedata = SqlQueue("data/tmp/async_js_sr.queue.db")


while True:
    print(voicedata.get())
