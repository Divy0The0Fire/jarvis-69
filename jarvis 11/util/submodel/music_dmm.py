"""Music Decision Making Model - Controls music playback and management"""
import os, sys
sys.path.append(os.getcwd())

from modules.llm_fn_call.blueprint.one_param import Fn, generateSystemPrompt
from modules.prompt.base import Prompt, Role, File, Image, Text, Function
from textwrap import dedent
from rich import print

functions = [
    Fn(
        name="play",
        description=dedent(
            """
            Play a song by name. If the song doesn't exist locally, it will be downloaded from YouTube.
            Parameters:
                song_name (str): Name of the song to play or YouTube search query
            """
        ),
        parameter={"song_name": "string"}
    ),
    Fn(
        name="pause",
        description=dedent(
            """
            Pause the currently playing song.
            Parameters:
                do_pause (bool): always True
            """
        ),
        parameter={"do_pause": "bool"}
    ),
    Fn(
        name="unpause",
        description=dedent(
            """
            Resume playing the paused song.
            Parameters:
                do_unpause (bool): always True
            """
        ),
        parameter={"do_unpause": "bool"}
    ),
    Fn(
        name="stop",
        description=dedent(
            """
            Stop the currently playing song.
            Parameters:
                do_stop (bool): always True
            """
        ),
        parameter={"do_stop": "bool"}
    ),
    Fn(
        name="loop",
        description=dedent(
            """
            Toggle song looping.
            Parameters:
                do_loop (bool): always True
            """
        ),
        parameter={"do_loop": "bool"}
    ),
    Fn(
        name="volume",
        description=dedent(
            """
            Set the playback volume.
            Parameters:
                level (int): Volume level between 0 and 1
            """
        ),
        parameter={"level": "int"}
    ),
    Fn(
        name="print_text",
        description=dedent(
            """
            To print a message to user
            Parameters:
                message (str): The message to print
            """
        ),
        parameter={"message": "string"}
    ),
]

systemPromptTemplate = Prompt(
    template=[
        generateSystemPrompt(functions),
        "YOUR LAST RESPONSE IS IMPORTANT WHAT EVER YOU DO IT MUST BE SHORTLY EXPLAINED TO USER, Example the song has been paused, playing xyz, No song is playing, etc.",
    ]
)



if __name__ == "__main__":
    from modules.llm._cohere import Cohere, COMMAND_R_PLUS, Model, ModelType, Role
    from modules.music_player.main import MusicPlayer
    
    p = MusicPlayer(r"modules\music_player\downloads")
    systemPromptTemplate.template.extend(
        [
            "THIS IS THE CURRENT STATUS OF THE MUSIC PLAYER",
            Function(
                p.get_playlist
            ),
            Function(
                p.get_status
            )
        ]
    )
    
    llm = Cohere(model=COMMAND_R_PLUS, systemPrompt=systemPromptTemplate.prompt)
    while True:
        query = input("Music Command >>> ")
        if query == "exit":
            break
        response = llm.run(query)
        print(response)