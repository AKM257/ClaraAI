from google import genai

client = genai.Client(api_key="AIzaSyCEeVe7TUgtPbQtE_2EShgxoer291wmLQk")

for model in client.models.list():
    print(model.name)