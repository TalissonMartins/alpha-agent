import os
from dotenv import load_dotenv
from google import genai

# Carrega a chave do ficheiro .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print(
        "❌ Erro: GEMINI_API_KEY não foi encontrada no ficheiro .env! Verifica"
        " se guardaste o ficheiro."
    )
else:
    client = genai.Client(api_key=api_key)

    print("--- AlphaAgent: A testar a ligação com a IA do Google ---")

    prompt = (
        "Responde em uma frase curta: Qual a importância da análise"
        " fundamentalista para investir na B3?"
    )

    try:
        # Modelo recomendado pelo próprio retorno da API do Google
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        print("\n🤖 Resposta do Gemini:")
        print(response.text)
        print("\n✅ Conexão estabelecida com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro ao conectar com o Gemini: {e}")