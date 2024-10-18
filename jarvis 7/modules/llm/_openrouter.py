try:
    from modules.llm.base import LLM, Model, ModelType, Role
except ImportError:
    import os
    import sys
    
    sys.path.append(os.path.dirname(__file__))
    from base import LLM, Model, ModelType, Role

from typing import Optional, List, Dict, Generator
from dotenv import load_dotenv
from rich import print
from copy import deepcopy

import os
import openai

load_dotenv()

LLAMA_VISION_FREE = Model(name="meta-llama/llama-3.2-11b-vision-instruct:free", typeof=ModelType.textandimage)
HERMES_3_LLAMA_3_1_405B = Model(name="nousresearch/hermes-3-llama-3.1-405b:free", typeof=ModelType.textonly)


# TODO: Add more models here

class Openrouter(LLM):
    def __init__(
        self,
        model: Model,
        apiKey: Optional[str] = None,
        messages: List[Dict[str, str]] = [],
        temperature: float = 0.0,
        systemPrompt: Optional[str] = None,
        maxTokens: int = 2048,
        cheatCode: Optional[str] = None,
        logFile: Optional[str] = None,
        extra: Dict[str, str] = {},
    ):
        super().__init__(model, apiKey, messages, temperature, systemPrompt, maxTokens, logFile)
        
        self.extra = extra
        self.cheatCode = cheatCode
        self.client: openai.OpenAI = self.constructClient()
        
        if cheatCode is None:
            p = self.testClient()
            if p:
                self.logger.info("Test successful for Openai API key. Model found.")
        else:
            self.logger.info("Cheat code provided. Model found.")

    def constructClient(self):
        try:
            client = openai.OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"] if self.apiKey is None else self.apiKey,
            base_url="https://openrouter.ai/api/v1"
            )
            return client
        except Exception as e:
            print(e)
            self.logger.error(e)
    
    def testClient(self) -> bool:
        try:
            modelListResponse = self.client.models.list()
            models = modelListResponse.data
            for modelinfo in models:
                if modelinfo.id == self.model.name:
                    break
            else:
                self.logger.error("Model not found")
                raise Exception("Model not found in OpenAI, please add it to the code.")
            return True
        except Exception as e:
            print(e)
            self.logger.error(e)
    
    def streamRun(self, prompt: str = "", imageUrl: Optional[str] = None, save: bool = True) -> Generator[str, None, None]:
        toSend = []
        if save and prompt:
            self.addMessage(Role.user, prompt, imageUrl)
        elif not save and prompt:
            toSend.append(self.getMessage(Role.user, prompt, imageUrl))

        try:
            extra = {}
            if self.cheatCode is not None:
                extra["seed"] = 0

            chat_completion = self.client.chat.completions.create(
                messages=self.messages + toSend,
                model=self.model.name,
                temperature=self.temperature,
                max_tokens=self.maxTokens,
                stream=True,
                **extra,
                **self.extra
            )
        except Exception as e:
            self.logger.error(e)
            return "Please check log file some error occured."
        
        final_response = ""
        
        for completion in chat_completion:
            if completion.choices[0].delta.content is None:
                self.logger.info(completion)
                break

            if completion.choices[0].delta is not None:
                final_response += completion.choices[0].delta.content
                yield completion.choices[0].delta.content
        if save:
            self.addMessage(Role.assistant, final_response)

    def run(self, prompt: str = "", imageUrl: Optional[str] = None, save: bool = True) -> str:
        toSend = []
        if save and prompt:
            self.addMessage(Role.user, prompt, imageUrl)
        elif not save and prompt:
            toSend.append(self.getMessage(Role.user, prompt, imageUrl))

        try:
            extra = {}
            if self.cheatCode is not None:
                extra["seed"] = 0

            chat_completion = self.client.chat.completions.create(
                messages=self.messages + toSend,
                model=self.model.name,
                temperature=self.temperature,
                max_tokens=self.maxTokens,
                **extra,
                **self.extra
            )
        except Exception as e:
            self.logger.error(e)
            return "Please check log file some error occured."

        log_completion = deepcopy(chat_completion)
        log_completion.choices[0].message.content = log_completion.choices[0].message.content[:20]
        self.logger.info(log_completion)

        
        if save:
            self.addMessage(Role.assistant, chat_completion.choices[0].message.content)
        
        
        return chat_completion.choices[0].message.content


if __name__ == "__main__":
    llm = Openrouter(HERMES_3_LLAMA_3_1_405B)
    # for i in llm.streamRun("do you like pizza"):
    #     print(i)
    
    
    while True:
        i = input(">>> ")
        llm.run(i)
    
    
    # llm.addMessage("user", "Hello, how are you?")
    # llm.addMessage("assistant", "I'm doing well, thank you!")
    # print(llm.run())
    # r = llm.run("what is in the image", "data:image/webp;base64,UklGRmoSAABXRUJQVlA4IF4SAAAQTgCdASoNAZsAPqlMoEwmJCaypxRbmlAVCUAxCkG9hA/Sk3vFKb2cjZn/NzT3E/tWbYDX5SqzEeN7/z7z9t/ZaEDqjhtOqk6fhRi9VXpujAFaHiWURoOvqw0iI8yh35Cjp25GIWwGPFBM0DTcTalDvHXrk47627V+7V6WTBTr1eWqpkhdxmtgoki1HIGOeYj0Vevkovabf7LGeztmoGmuvS4tWwOye41mliprkIWzS4wxW7LVgEgfrDR2QdiK2qz6Jxw2CeB30YEYt0OIlBx4OZR9YQ2Bgt7KH7Q8dEeehq4t5FG5ea+0cXloZEhNwKjhaHJB3hr5P2Vdy5XC0fu69GjwcqkK3oTKng+v3LWmTW4wPOMvtpNuzUBffmoB+VwUPLycnt4hmDuIiqt//CHGx2yFKvtrAFeBS1zumsnDtv7HnyuROIix3mwthE/lw/0qCJdMWN0yxtEjKy3YWzfdQB3UUb4KH8oMftOeYADnvUl52s6myy/a6+G1raT9n7aND1I1njppIRQakNPZmYoafwgk3GFu3lQLF4fTSP/dzCkC2pCj4rB7523mvHfLAfmquDMQyRIacuvF+6OF2pp9Pr7nIXeLh3XN0fy2YXsigSivN/vqrCCHU16UgIZLLWKfkgdg6Rm+Rn9hdSHqtvpJmtpKaPowEudNtaJP2cmcA4l7ojdKTrg4kNWMobiDrEfK8vC8Ul3Umr7QguparNJGZhjJp+s5KD47PEid22Q3PRjkc3vrHgxk7FXBmSvQJrP8Ygry/iMWdqU00kCY/l7D/ZHy+imW5vPZCZRLYlPMwxDwgAdYe2K38s9AFNyzY+5ARnrL+gLExQAA/t4+w8v+cGgracr16DNmV8V2q5FK7pEm0GbLJpzhl29CW5jteLC/S88KvmR5LZEtaKHusCWlUZxvGoH/mvDs9XeTPWHsfb0L783z9NvxAPtCaU6Q+23R5q5RqOc4PHiJZM5deCnL6xN1RUILqIVw8FBnx1DTSf9h8DQ9qtVD0KtFdDkuLZTqAA5oFt1GeGvgZD9DTbT1hPLOPaHg/PiZ/xdufDVzXUL/Gj5O6C7znXlYPlkp19KkkVhIhxPYrM1/hbm1WoVF0W8INd3fJ5pmdl1qtMVRQNQaYqABOZGOH6R/zr7Oed1wMvD9SJ3wgN9/66QF9zFg5VioNlfMN1g6ELitMeIQ58/UXtxPHa8glWFZyk8bmVKnC3wCYrScG0nBRnXT7fBx6HiCkppXDW5yafLFnc6qr6emOyUprplq8QGY8jTgdNee51XUcG8yrieyUL3qaroRnzxR4JBwWBormcUltujWJ0MFRk7sgRKI/wtHdv8fZM7IN9EqlBspfXSiAIJnA9ZCV+7K8ZAm8d38+ey5ODRLZvV+e+7s1uGGhF5i8csJLkB4uODt369GrWa6k8t8WME8HSxImwBV+zPcaXvRnY5+MsuNBgHefeioaCUHrqTg1G2hDuYCX/eyWWsCwMaQ1r4GapLN/EucaWmW8TdrvXzbdvsIGaEDg56XbffihbhgGbUw1HEcVc9qP13LrguDn+NeYePLnilUA55ug9MDoDacsJQRNIbLZFfs+D+YolTlC28CTRoTOHdd85ni3PFBGlD/GZYxrnXJgoKpf2GzWqG+GlMgPJb2y1bVRvPn4n+ATR92XWFMjuzw3andF8nPGMehgjEfBET0vKS5wip4wHG5yNdwzG834lKSk6vM/OJ1X8ArjMWRt6n6F6a6MdDvU/nIRLQjufC7MQwu+eDlo3MZsEGvGM1w9BuDqhV23ksdT/Pow3v1Ogw/qP2BzrzeW+nrYd9FWdht/3RJitoisLFrqC1YD7Lkc9NzjpfxRoceg6znuptD0/K48cCbm0AxsRGahvPFUJ8ypAafzJ7XfuMMAPZqrjBQ3BrLK0SG6tU7X5dE2YjvjKB3RBOEbWaZV+02jR+SZnwdGz6SaqgVtEtZid+1U/mZA2rQlrVL7FHC4SMSXKc42ZP5KJXYrMQcbPItJeYKGvecmVCM/DE3tsjtlxx70sohv7m398f5B4BRlgGhSnLByHPpBTwTUp8rnsW0ozCdCG8+Gx5ocpbq3X1R0Kfqbw5rcMA2hzPMhG8m1xWbflSGzmSeI+aTkGtyPdCBGsow/I5i8yyyflis9acY4T3Bx5mnaNnL9W3I4lV526EZ7IvQei/Ltse+BNlnlYoXLpyXUVW8ai4xUM1fQ37gMWbUh6gAjLqbLLKjuiLFScpWevGVRnYEmImm3p+BOfKDtVlerj44JVmSkb7jnuE+0IF0o43PQs8hB6FFVgHrQCfvd5gGQeuMTL0n+ZcM7akcIUSHM3x9Y8XAecHO6GgoMBXgYDqSQ8Aya3Fdh77yw+OFx/TEkUDWhfZA0pQch6muXdjLAjtXb+d7um9WG+oF5537J3j7QbSebvJDliSV8ZdLoekEMyoEizHasGwRKrRbIVr5fdJX5V/CTtw79fMZCMacS+L4fRxjgvncgPEr1OG0AEgaJIfAxutDdCHapanf+BtuByBcePxoLkH5lG1LxITbRifyeII/IW0C3BuehNJEteQrsbQH15ohajCvoktR7A8pVO0JB9/ZL8sxuFjZz1dgHCWnMEuXlssnvLYXYe+wcg3N8jeYaPpzlCCfYAleFxmXJIa/2w81FDdCE9Wvu6EelgMODuoM0eE/A52TFC9Ay3VEc07AKwT2v7LYPAVwdi9icpTT5Lvxlg8UHPW279CqRGDaLUrgWYfPmcn9PgGKk83MDBJHRZhOlThfpRE9TK9aFfF5RNFeY9HvYB+n0diDE/EhRTPT+tuTqAKHqg12yPfBY4/lE9VEmH802w6MhE0JRYPaZdPZRnmLfgsj4O0IYWLECtLjyrrvpz4jffefOug5ndjKVQa4LZBF06dBlUYJF05fGdUvsi+hcSZUPencQF2CRT11sTt/H3gQXj3hZjHxtbnnFzpLPujJXUYFMdA3jBlMFUhErLynY1xGdoCynYuY6GteW+z4e5lQHxSJ8ClXE1ZsrkhEff56+8uT4lbuuA0thXJL/UARjTqeU48DUTjmqUi5RAnvOq0xYzm42U9jW8LHbP2xbpWFG4X0vl/ajDPnGQhaiEgxR+f9Ttn7rY5W0g9x56zM1U1OYr633sBlEil8F6j4VQEGSt9KqrTq5BYsbBFkn8aK45VA80sHK0w1sGLRJnJbUZEWdFhI8uj+1jd5mazpYCtX6LhGZ3OdDQExz8hR+hfGiUH/5pHSWsf7P202yS31lal6uyolmlYyrV8fBhaCe9tvS3vT6cjBoKw81nx+90an1qDwkWlVXtfLvHInSE22lJHU79mPleE2OvYXe0NyB6seEgFxbwabx4KjfZq5JUHWuINXsNw20M/WTKz5fG+wsNycX7UbcdW8du/syb1DpGXp4bjTtWi3YnFLmZFicLwGTigDaujWmqdPvo+VFS6bl0dY/p/5n0YBNJdr0A1aPGJ6KkgVnS7iLGLZNOOTG/z0BBmDfiuZnUWfdyHUJaPlnaCuzS5Tk/bvIlVq1z8nHDzgyYO/u3XWQzCQIDWRFs4cpXF8kgVoXhcNjv6kJXQqsRrGNntV1CI5naI7L8zcQl09ik40IFCEKdDzQoX2Q0eoitUkuqFaaxnPjUrr0PqwADKOcaCvA0ceMI0tBkx0tTQpJoq+quaEuWHnoxNRuP58iSuugBSm608M6grOt7btMNffxFcOjcgRD3f4OJZJpvIwHGrGJVT3B6Wv458fZ0ViYFZRQ23WdfEmCE4UeAD6WKOYTfW64g6lMDDDULEMdY9fpHdzA6Vqa5UePy1wodUBhO9yFiN2PEFozmW4G8IoJVkpbob770RVLoPvvuG9bYsaf8RszoVejGrAD4by1xhbV/KPGR1pLJYiCxo/Umg/XPz0bHVueUQvO1Drz8SmcmFroy0nvWOUF+wiuj12izDD7AwrET8jSEqGCDb+QoAhxg0JYGoUs2tvaKpNzsDAN1xAer17LJG8OnmN5eXUY4Nt2jYTdfWGBj70a+nNtbd5jtDP/taGKdDmM8EoESFdD7sT6O8kwMNa6QHqr6bPaD0NLnkVAICHjQh4zFbFbuwrKQOtuOsg4+1+yyGNb8aZvth5QLe5Zk2Z5ZbHdpq5RnjrSPCOhIduM/dPTdbet9GHHCj1THbkiwtFpmmkagDpsmnF6gp9C9pVJkStrnpon7Q2fs1ybRagnZl8Z2c0LpbW+OXPen/kM3VKRi/aVq9NzDDdWgav4wpRW2oduA33ALfKfCIgB3FCvjrG401ZcztsK5TZgKwSG3D11Hguu4G1hylykJ/KFv7fbx1XfSvLrEXKJB2ToViB37aMz/SnRWa2XbrVX2AVYui/Wz8equ28G2NKasUTW4CldrlSPBYcxN+40ZClcbA4Kpah43riOXw8aK5CNDxia5GLoMVb8feSsdAft6NQasFpSHHi+CFxcG7sHaLAvLu4ET4oX15mDOQNJDhLS6+0fuHVe+Bb/A6QFxNtRJXtKTtjD8uC93efY7kMa/cYgtTu7HuunM/SJxbbsF8vsi441iIieiIuV+4HiXO2OlKkx6FAiZ+CL40Dbf25iV6e9sTs/T62/zFPVCjS+DFPT8dvLq4Z/OZJbspdulWCEcSo01uaKdkh0wXFTknrTD4Fsp0tXhoippmZp+tDiqgcpEP+BO2PTmUDBnIYRSzMwhcC+ttaPtCcZy0jnNrnbZqixn/XDLzjtK+0SnTaDRNcYi4rV/75Icg2lVBIWtCC37QB2x7fh2nXv2Eglxnxa6E9GTCasGZEUIsXkPi2De0KOBHUUSUqU4bLPEpEEws2cMWls+hAzyRpZscf9uwxjlqoawyKcWdjlXrgamGMgBFOWf4rNEXei8EJMijHZYAmiSUNcY2hhUkvrDmeE2mOHhiBCeUHyXcjCkQltZ30TF5hBJeDz1oqDSN5L8XR+WTuGNhZuk2/52U5yPvQvKZdWedbcqQieYN2wkmH+1nxYXQwrw74X0MR4OGYK4UJGUw1/1xX4AujwoTpPn/xl+0cFsvancOHqzNkF5O1EJ2wSObydaF2PVbVBOG00JHCAUJPPGiJdSi3cvo6loVupXGNVSayXNpm1fZLOeTvZvWY7BZF7B5ulWI+KRVBqiPWKZOBAnIqEKqUvKTIHeL5HbtjpG3GKd3YkNPUec3zU7LMzsa9CoiZVYR/OTE22BnfiUfEicoOAnQwA5xht0ySAz15iKGY2MgrgvNGeJEPf8AwVh5JD4/TpQIsbrJYXs+hHtLh2Gz3BhZnzJoiUQCI/HdikHJID2qOCTmtJLrVHCilcdQhyADanoawf92g8/0l9YUudsPxAPjst4wKID2xEVce7lANbmcWSh8Wpw6s+t2fv9f6mGYct0VcYAm/jQ1IojHkcgJH/c9vv1lvRW4l4Vzvzek2FsCS9PE06x8B46Oy+xRuak/6bEJkKkuYkSgxe73t9EZAD1yuZLsjw9lAVQ3XgG3IlVcn9Vb6c3VcArIBzefvTlRO8/JkW0v+y63c6C2n+0NY5Bl2QJvdDUV+l2jTUv8OP+FQUUFie9QNHRoHiyfat0SktH7EUhmjReg//DSNvA7dZFSV1tH53mUH09rsQSR9J4qXjArRi5CK8x9lCZ6kmmrKgdyy0t9I3zYOUN6741fSKtYihS2K6OSQGlprzDI1L5GYn+ZbTrSyLanMPSusb+PTVj+LAAKz5Rt5nVKhHMURonQRcqL5unPjbs+lpzPSf5o5dU9NncHlhLbuy60rIPP2xDjNm1Uy6PU0VB471/Qg9DsLHpkqy1rmTSkXqK0WeHiu0yHanAGaH1Z8ARpbR/vTgn1w5VKEPmiNXai7QLInkAgu8NgxsY5VxuzYbYh0kz2vUbxdpWHAtySsgCt8VtLmJJtfhbFGqSPuPHbWcSoIdBZcjvrC9A/PY+ZT/rCTkwrlPO8CQ8uSkd+c8vJUpwky7Nwg2kTcFYb3mwY71zgBUmR1juXywCO9d53VWaibVNVqooLL+X1LsgsiiS0R9YhrXZiUCx1Sej8fsKGP9lCh8F5HdmoajrbXfNWqYNOuWX7pOY87oACyktnWCpvpgxoM7rVrDfChPN5SDIq4tMg/k3WFcfxGw43qj0wonK0QOrh5N+IL4iHoUKfdubThvsfj0x5RE0WDC79j4WMxXnM9uvCtYU86vf+I6lgwTxaBmTFUGmR3wSd48RkfMgo44xhWHf0h6YojisojlXzvePQe0Y7IaOgHxi+j6IfrDJROiESeheQyB8GLYKnZAAAA")
    # print(llm.messages)
    # print(r)
    