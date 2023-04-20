import torch
import clip
from PIL import Image
import requests
from io import BytesIO
import numpy as np

# Load the CLIP model and processor
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Function to generate captions for an image given its URL


# Function to generate captions for an image given its URL
def generate_caption(image_url):
    response = requests.get(image_url, verify=False)
    image = Image.open(BytesIO(response.content)).convert("RGB")
    image_input = preprocess(image).unsqueeze(0).to(device)

    # Predefined list of words to generate the caption
    words = ["a", "photo", "of", "a", "dog", "cat", "bird", "car",
             "building", "tree", "person", "food", "city", "beach", "landscape"]
    prompt = clip.tokenize(words).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image_input)
        text_features = model.encode_text(prompt)

        # Compute the similarity between image and text embeddings
        logits_per_image = image_features @ text_features.t()
        probs = logits_per_image.softmax(dim=-1).cpu().numpy()

    # Generate the caption
    captions = ["a", "photo", "of", "a"]
    for _ in range(5):
        word_index = np.argmax(probs[0])
        word = words[word_index]
        captions.append(word)
        words.remove(word)
        prompt = clip.tokenize(words).to(device)

        with torch.no_grad():
            text_features = model.encode_text(prompt)
            logits_per_image = image_features @ text_features.t()
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()

    caption = " ".join(captions)

    return caption


if __name__ == "__main__":
    # Generate a caption for an image
    image_url = "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__340.jpg"
    caption = generate_caption(image_url)
    print(caption)
