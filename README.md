# RAG-based-QA-Bot
this repo consist of RAG based Question answering system 


##### Steps 

1. download the requirements and create virtual environment
2. have the python version of 3.11 this is considered to be stable version
3. create pdf_util.py for chunking the pdf and previewing it
4. in .env file create your own api key ie by using Groq or Openai etc
5. in config.py we implement the basic chatbot that has model name and api key imported from .env file by using dotenv()
6. Since computer can only understand numbers not alphabets we use embeddings ie model used here is sentence-transformers that converts word to number
7. By using the above step we create vector db that store texts, meta data here the vector db is Chroma db used
8. for the front end we use gradio


##### cammands 

1. `python -m venv venv` - creating virtual environment
2. `pip install -r requirements.txt` - installing requirements
3. `python app.py` - running the working directory


###### Output:

1. cammand

   <img width="1610" height="330" alt="image" src="https://github.com/user-attachments/assets/670770e1-6c02-4c33-a0d1-b5313d99fd78" />



2. Frontend

   <img width="1542" height="962" alt="image" src="https://github.com/user-attachments/assets/db8dd1b4-f806-4a4e-9d2a-1e1c4e047b2e" />

3. Working images

   <img width="1091" height="820" alt="image" src="https://github.com/user-attachments/assets/206a86d5-c1cb-49a1-8d87-d95c257dcfc0" />

   <img width="961" height="735" alt="image" src="https://github.com/user-attachments/assets/fe2315a0-aa6a-4f83-a591-9141ff6546e8" />

4. If the question was asked outside the scope then it won't answer

   <img width="1057" height="561" alt="image" src="https://github.com/user-attachments/assets/42b64f6a-6122-42fb-9c07-665113d7478c" />



