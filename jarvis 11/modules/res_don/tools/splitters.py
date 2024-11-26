# Configuration optimized for accuracy
class RecursiveCharacterTextSplitter:
    """
    A text splitter that divides text into overlapping chunks of specified size.

    Parameters
    ----------
    chunkSize : int, optional
        The size of each text chunk in characters, by default 1200
    chunkOverlap : int, optional
        The number of characters to overlap between chunks, by default 200

    Attributes
    ----------
    chunkSize : int
        Stored chunk size value
    chunkOverlap : int
        Stored chunk overlap value
    """
    def __init__(self, chunkSize: int = 1200, chunkOverlap: int = 200) -> None:
        self.chunkSize = chunkSize
        self.chunkOverlap = chunkOverlap

    def splitText(self, text: str) -> list[str]:
        """
        Split input text into overlapping chunks.

        Parameters
        ----------
        text : str
            The input text to be split into chunks

        Returns
        -------
        list[str]
            A list of text chunks with specified size and overlap
        """
        chunks: list[str] = []
        start: int = 0
        
        # Loop to create overlapping chunks
        while start < len(text):
            end: int = start + self.chunkSize
            chunk: str = text[start:end]
            chunks.append(chunk.strip())
            
            # Move the start position forward by chunk_size - chunk_overlap
            start += self.chunkSize - self.chunkOverlap
            
            # If a partial chunk at the end is too small, we break out of the loop
            if start >= len(text) and len(chunk) < self.chunkSize:
                break

        return chunks

if __name__ == "__main__":
    splitter = RecursiveCharacterTextSplitter(chunkSize=1200, chunkOverlap=200)


    large_document_text = """
    Cupidatat officia eu voluptate eiusmod non. Sit cupidatat occaecat est enim. Dolor dolore reprehenderit ipsum dolore dolor nostrud reprehenderit minim. Adipisicing est esse nulla eu eu exercitation Lorem eu magna do elit labore. Elit irure id tempor anim excepteur deserunt nostrud consectetur culpa officia.

    Duis esse excepteur dolor duis. Exercitation laboris laborum ullamco exercitation proident amet reprehenderit dolore nulla tempor. Commodo elit non elit ad culpa fugiat.

    Eu nostrud do cillum cupidatat ut ex proident. Tempor dolore consectetur qui qui ea in et sit aliqua reprehenderit. Minim enim aliquip culpa est eiusmod eiusmod velit anim. Eu sit excepteur quis labore culpa occaecat tempor sint laborum.

    Esse est Lorem cupidatat ut qui pariatur incididunt dolore dolore reprehenderit proident ea ullamco. Aliqua et nisi esse do sunt duis eu voluptate mollit in. Aliqua aliqua eu do anim quis amet dolore Lorem dolor mollit minim. Magna labore voluptate mollit ex ullamco incididunt pariatur magna aliqua veniam aliqua esse. Ut aute eu fugiat velit fugiat Lorem. Adipisicing do aliqua incididunt nisi dolor dolore cupidatat exercitation aute aute labore veniam cillum fugiat. Incididunt exercitation commodo aliquip minim voluptate.

    Qui consequat fugiat veniam reprehenderit sint mollit amet esse qui esse. Lorem veniam voluptate ex duis cillum ex in in. Aliquip officia qui ipsum ullamco cillum proident. Labore aute sit aliquip cillum non deserunt cillum reprehenderit cupidatat ut.

    In laboris Lorem nostrud cupidatat irure fugiat veniam ad ullamco. Quis Lorem consectetur anim irure quis. Ut dolore veniam velit magna eiusmod aute culpa deserunt. Nulla consectetur aute excepteur aliqua non minim adipisicing incididunt consectetur ea consectetur irure.

    Commodo ipsum Lorem sit dolore ea fugiat. Dolor sint veniam adipisicing quis labore amet dolore consectetur ipsum. Enim sit magna sunt dolore id eu mollit commodo Lorem. Ullamco irure incididunt commodo tempor ipsum qui do elit irure anim reprehenderit in sunt. Minim ex magna ad cillum labore cupidatat cupidatat consequat nulla anim aliqua nisi consectetur id. Esse adipisicing consequat proident proident est consectetur aute pariatur duis magna cillum ad aliquip exercitation. Adipisicing id minim adipisicing sint esse ut.

    Ad amet esse adipisicing aute velit esse id sint laboris esse fugiat aliqua. Eu ea ex quis cillum et aute dolore sint deserunt veniam. Sit ex nisi adipisicing non esse cupidatat duis eu. Mollit exercitation ipsum aliquip reprehenderit laborum dolore tempor eiusmod et dolore ullamco. Aliqua cupidatat in consequat ut sint magna aliquip. Quis pariatur mollit eiusmod commodo fugiat et aliqua velit quis.

    Ipsum do elit Lorem sunt laboris incididunt nulla fugiat ut officia ad magna reprehenderit. Nisi occaecat laborum esse labore. Ad ut esse voluptate dolore dolore amet nulla aliqua deserunt anim est.

    Minim est culpa et eiusmod elit laboris laborum exercitation aliquip adipisicing sunt ex. Do officia esse voluptate tempor cillum consectetur et sunt amet quis reprehenderit. Cupidatat duis sunt occaecat cupidatat. Aliqua nisi occaecat Lorem ad fugiat pariatur mollit fugiat cillum nostrud.
    """

    # Split the text into chunks
    text_chunks = splitter.splitText(large_document_text)


    # Process each chunk for accurate analysis
    for chunk in text_chunks:
        print(">>>", chunk)
        # Store, log, or further process the response as needed
