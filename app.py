import json
import urllib.request
import urllib.error
from flask import Flask, request, jsonify

app = Flask(__name__)

GEMINI_API_KEY = "AQ.Ab8RN6L9zoSw0xfy4oQI8T-zR6gu2s88_-9GC0E--g4Rg5i9Gw"

@app.route('/webhook', methods=['POST'])
def cualificar_lead():
    data = request.get_json() or {}
    mensaje = data.get("mensaje", "")

    prompt = f"""
    Eres el asistente de cualificación de leads de Vortex Media.
    Analiza el siguiente mensaje de un cliente potencial y determina su intención de compra.

    Mensaje: "{mensaje}"

    Responde ÚNICAMENTE en formato JSON estricto con las siguientes llaves:
    - "estado": "ALTA INTENCIÓN" o "CONSULTA GENERAL"
    - "razon": Una breve explicación de por qué clasificaste así el mensaje.
    - "accion": "Redirigir a asesor humano" o "Responder con bot de preguntas frecuentes"
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    headers = {'Content-Type': 'application/json'}

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            texto = res_data['candidates'][0]['content']['parts'][0]['text']

            if "```json" in texto:
                texto = texto.split("```json")[1].split("```")[0]
            elif "```" in texto:
                texto = texto.split("```")[1].split("```")[0]

            resultado = json.loads(texto.strip())
            return jsonify(resultado), 200

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print("Error HTTP de Google:", e.code, error_body)
        return jsonify({
            "error": "Google API error",
            "status_code": e.code,
            "detail": error_body
        }), 500

    except Exception as e:
        print("Error en el servidor:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
