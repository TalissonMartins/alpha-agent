import os

from dotenv import load_dotenv
from google import genai


def main() -> int:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Erro: GEMINI_API_KEY não foi encontrada no ficheiro .env.")
        return 1

    client = genai.Client(api_key=api_key)
    prompt = (
        "Responde em uma frase curta: Qual a importância da análise"
        " fundamentalista para investir na B3?"
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
    except Exception as e:
        print(f"Erro ao conectar com o Gemini: {e}")
        return 1

    print("\nResposta do Gemini:")
    print(response.text)
    print("\nConexão estabelecida com sucesso!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
