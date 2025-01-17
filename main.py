import os
from openai import OpenAI
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)
client = OpenAI()

# DALL·E APIの設定
dalle_api_key = os.getenv("OPENAI_API_KEY")

@app.route('/generate-and-upload', methods=['POST'])
def generate_and_upload():
    try:
        # プロンプトを受け取る
        data = request.json
        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # DALL·E 3のAPIを叩いて画像を生成
        client.api_key = dalle_api_key
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1792x1024",
            quality="standard"
        )

        # レスポンスをJSON形式に変換
        json_response = json.loads(response.model_dump_json())

        # 画像を保存するディレクトリを設定
        image_dir = os.path.join(os.curdir, 'images')
        if not os.path.isdir(image_dir):
            os.mkdir(image_dir)

        # 画像の保存と処理
        image_path = os.path.join(image_dir, 'headwaters.png')
        image_url = json_response["data"][0]["url"]
        generated_image = requests.get(image_url).content

        with open(image_path, "wb") as image_file:
            image_file.write(generated_image)

        # MicroCMSへのアップロード
        headers = {
            'X-MICROCMS-API-KEY': os.getenv("MICROCMS_API_KEY"),
        }
        files = {
            "file": ("headwaters.png", open("images/headwaters.png", "rb"), "image/png")
        }

        response = requests.post('https://vwu4v7j6wa.microcms-management.io/api/v1/media', headers=headers, files=files)
        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)