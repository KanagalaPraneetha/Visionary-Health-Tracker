from openai import OpenAI
import cloudinary
import cloudinary.uploader
import cloudinary.api

class VisionAPI:
    def __init__(self):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name="dg0u5ptwr",
            api_key="131772664789931",
            api_secret="8GQoqex1PntyUkR2E2V7HeG7wGw"
        )
        
        # Configure OpenAI client
        self.client = OpenAI(
            base_url="https://api.studio.nebius.ai/v1/",
            api_key="eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwNzE2MzI4NDkzNTM1MzY2Mzc1NiIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIiwiaXNzIjoiYXBpX2tleV9pc3N1ZXIiLCJhdWQiOlsiaHR0cHM6Ly9uZWJpdXMtaW5mZXJlbmNlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIl0sImV4cCI6MTg5NDMwNjM1MCwidXVpZCI6ImRiMzY2YWI3LTJjODEtNGVkZS1hYzZiLWY5Njg5MDgwYWQ1MyIsIm5hbWUiOiJIYWNrYXRob24iLCJleHBpcmVzX2F0IjoiMjAzMC0wMS0xMFQyMDoxMjozMCswMDAwIn0.Uqxspooor2Xnrzp6uoTnqvp3uwZW50M9uTklgkDPtoo"
        )

    def upload_to_cloudinary(self, file):
        try:
            upload_result = cloudinary.uploader.upload(file)
            return upload_result.get("url")
        except Exception as e:
            raise Exception(f"Image upload failed: {str(e)}")

    def analyze_image(self, image_url):
        response = self.client.chat.completions.create(
            model="Qwen/Qwen2-VL-72B-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "If the image is about food, provide nutritional information and recommend healthier alternatives if not food give me information of item or object if its a person give me mood of the person."},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content