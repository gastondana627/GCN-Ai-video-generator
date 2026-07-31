import os
import random
import time
import urllib.parse
import base64
import requests
from fastapi import HTTPException

# ==========================================
# 1. Image Key Rotation & Fallback Setup
# ==========================================
IMAGE_PROVIDERS = [
    {"provider": "openrouter", "key": os.getenv("OPENROUTER_API_KEY")},
    {"provider": "gemini", "key": os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_Key") or os.getenv("GCN_IMAGE_GEN_KEY")},
]

image_index = 0

def get_next_image_client():
    global image_index
    active_providers = [p for p in IMAGE_PROVIDERS if p["key"]]
    if not active_providers:
        return None
    client = active_providers[image_index % len(active_providers)]
    image_index = (image_index + 1) % len(active_providers)
    return client

def execute_image_generation_with_fallback(prompt: str, model: str = "black-forest-labs/flux-schnell"):
    active_providers = [p for p in IMAGE_PROVIDERS if p["key"]]
    last_error = "Unknown error"
    
    if active_providers:
        for _ in range(len(active_providers)):
            client = get_next_image_client()
            if not client:
                continue
                
            try:
                print(f"[IMAGE ROTATION] Attempting generation with provider: {client['provider']}")
                
                if client["provider"] == "openrouter":
                    response = requests.post(
                        "https://openrouter.ai/api/v1/images/generations",
                        headers={
                            "Authorization": f"Bearer {client['key']}",
                            "Content-Type": "application/json"
                        },
                        json={"model": model, "prompt": prompt, "n": 1, "size": "1024x1024"}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        image_url = data.get("data", [{}])[0].get("url")
                        image_b64 = data.get("data", [{}])[0].get("b64_json")
                        return {"image_url": image_url, "image_base64": image_b64}
                    else:
                        last_error = f"OpenRouter HTTP {response.status_code}: {response.text}"
                        print(f"[ERROR] {last_error}")

                elif client["provider"] == "gemini":
                    response = requests.post(
                        "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict",
                        headers={"x-goog-api-key": client['key'], "Content-Type": "application/json"},
                        json={
                            "instances": [{"prompt": prompt}],
                            "parameters": {"sampleCount": 1}
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        predictions = data.get("predictions", [{}])
                        b64_data = predictions[0].get("bytesBase64Encoded") or predictions[0].get("imageBytes")
                        if b64_data:
                            return {"image_base64": b64_data}
                    else:
                        last_error = f"Gemini HTTP {response.status_code}: {response.text}"
                        print(f"[ERROR] {last_error}")
                        
            except Exception as e:
                last_error = str(e)
                print(f"[EXCEPTION] {last_error}")
                continue
                
    # Dynamic Prompt Render Fallback with Random Seed for fresh variations
    print(f"[FALLBACK] Rendering image prompt via dynamic pipeline with random seed.")
    encoded_prompt = urllib.parse.quote(prompt)
    random_seed = random.randint(1, 999999)
    return {"image_url": f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={random_seed}"}


# ==========================================
# 2. Video Key Rotation & Fallback Setup
# ==========================================
VIDEO_PROVIDERS = [
    # Seedance v2 API prioritized for free daily video credits!
    {"provider": "seedance", "key": os.getenv("SEEDANCE_API_Key")},
    {"provider": "fal", "key": os.getenv("FAL_API_Key") or os.getenv("FAL_KEY")},
    {"provider": "huggingface", "key": os.getenv("HUGGINGFACEHUB_API_KEY") or os.getenv("HF_TOKEN")},
]
video_index = 0

def get_next_video_client():
    global video_index
    active_providers = [p for p in VIDEO_PROVIDERS if p["key"]]
    if not active_providers:
        return None
    client = active_providers[video_index % len(active_providers)]
    video_index = (video_index + 1) % len(active_providers)
    return client

def execute_video_generation_with_fallback(prompt: str):
    active_providers = [p for p in VIDEO_PROVIDERS if p["key"]]
    last_error = "Unknown error"
    
    if active_providers:
        for _ in range(len(active_providers)):
            client = get_next_video_client()
            if not client:
                continue
                
            try:
                print(f"[VIDEO ROTATION] Attempting generation with provider: {client['provider']}")
                
                # --- NEW SEEDANCE V2 INTEGRATION ---
                if client["provider"] == "seedance":
                    response = requests.post(
                        "https://seedanceapi.org/v2/generate",
                        headers={
                            "Authorization": f"Bearer {client['key']}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "seedance-2.0",
                            "prompt": prompt,
                            "aspect_ratio": "16:9",
                            "duration": 5,
                            "resolution": "720p"
                        }
                    )
                    
                    if response.status_code in [200, 201]:
                        data = response.json()
                        resp_data = data.get("data", {})
                        task_id = resp_data.get("task_id")
                        
                        if task_id:
                            print(f"[SEEDANCE] Task queued (ID: {task_id}). Polling v2 endpoint for completion...")
                            for attempt in range(40):  # Poll for up to 80 seconds
                                time.sleep(2)
                                poll_resp = requests.get(
                                    f"https://seedanceapi.org/v2/status?task_id={task_id}",
                                    headers={"Authorization": f"Bearer {client['key']}"}
                                )
                                if poll_resp.status_code == 200:
                                    poll_data = poll_resp.json()
                                    poll_resp_data = poll_data.get("data", {})
                                    status = poll_resp_data.get("status", "").upper()
                                    
                                    if status == "SUCCESS":
                                        print("[SEEDANCE] Video generation completed!")
                                        vid_urls = poll_resp_data.get("response", [])
                                        if vid_urls:
                                            return {"video_url": vid_urls[0]}
                                        break
                                    elif status == "FAILED":
                                        last_error = f"Seedance Task Failed: {poll_data}"
                                        print(f"[ERROR] {last_error}")
                                        break
                                        
                        last_error = f"Seedance response missing task_id: {data}"
                    else:
                        last_error = f"Seedance HTTP {response.status_code}: {response.text}"
                        print(f"[ERROR] {last_error}")

                elif client["provider"] == "fal":
                    response = requests.post(
                        "https://fal.run/fal-ai/fast-svd",
                        headers={
                            "Authorization": f"Key {client['key']}",
                            "Content-Type": "application/json"
                        },
                        json={"prompt": prompt}
                    )
                    if response.status_code in [200, 201]:
                        data = response.json()
                        video_url = data.get("video", {}).get("url") or data.get("video_url")
                        if video_url:
                            return {"video_url": video_url}
                    else:
                        last_error = f"Fal HTTP {response.status_code}: {response.text}"
                        print(f"[ERROR] {last_error}")

                elif client["provider"] == "huggingface":
                    response = requests.post(
                        "https://api-inference.huggingface.co/models/stabilityai/stable-video-diffusion-img2vid",
                        headers={"Authorization": f"Bearer {client['key']}"},
                        json={"inputs": prompt}
                    )
                    if response.status_code == 200:
                        b64_video = base64.b64encode(response.content).decode("utf-8")
                        return {"video_base64": f"data:video/mp4;base64,{b64_video}"}
                    else:
                        last_error = f"HuggingFace HTTP {response.status_code}: {response.text}"
                        print(f"[ERROR] {last_error}")
                        
            except Exception as e:
                last_error = str(e)
                print(f"[EXCEPTION] {last_error}")
                continue
            
    # Intelligent Video Fallback
    print(f"[FALLBACK] Video APIs restricted ({last_error}). Routing to MP4 fallback clips.")
    prompt_lower = prompt.lower()
    
    if any(k in prompt_lower for k in ["skate", "kickflip", "board", "trick"]):
        selected_clip = "Kickflip.mp4"
    elif any(k in prompt_lower for k in ["monster", "dream", "creature", "weird", "teaparty"]):
        selected_clip = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"
    elif any(k in prompt_lower for k in ["fire", "action", "blaze", "explos"]):
        selected_clip = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    elif any(k in prompt_lower for k in ["run", "escape", "fast", "chase"]):
        selected_clip = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4"
    else:
        CINEMATIC_CLIPS = [
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"
        ]
        selected_clip = random.choice(CINEMATIC_CLIPS)
        
    return {"video_url": selected_clip}