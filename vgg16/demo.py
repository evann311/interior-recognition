import json
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from keras.models import Model
from sklearn.metrics.pairwise import cosine_similarity
import argparse

train_data_dir = '../data/train'
model_path = 'vgg16_places365_finetuned_final.keras'
class_indices_path = 'class_indices.json'


model = load_model(model_path)

feature_extractor = Model(inputs=model.input, outputs=model.layers[-3].output)  # Lớp GlobalAveragePooling2D


def load_and_preprocess_image(img_path, target_size=(224, 224)):
    img = load_img(img_path, target_size=target_size)
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Rescale
    return img_array

with open(class_indices_path, 'r') as f:
    class_indices = json.load(f)
class_indices = {int(v): k for k, v in class_indices.items()}

input_image_path = '../data/test/U/image_7.png'

def predict(input_image_path):
    input_image = load_and_preprocess_image(input_image_path)
    predicted_class = np.argmax(model.predict(input_image))

    predicted_class_name = class_indices[predicted_class]

    input_feature = feature_extractor.predict(input_image)

    image_paths = []
    features = []
    class_dir = os.path.join(train_data_dir, predicted_class_name)

    for img_name in os.listdir(class_dir):
        if img_name.lower().endswith(('png', 'jpg', 'jpeg')):
            img_path = os.path.join(class_dir, img_name)
            img = load_and_preprocess_image(img_path)
            feature = feature_extractor.predict(img)
            image_paths.append(img_path)
            features.append(feature)

    features = np.vstack(features)

    similarities = cosine_similarity(input_feature, features)
    most_similar_index = np.argmax(similarities)
    most_similar_image_path = image_paths[most_similar_index]

    print(f"The most similar image in class {predicted_class_name} is: {most_similar_image_path}")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Interior Detection')
    parser.add_argument('--input', type=str, help='Path to the input image')
    args = parser.parse_args()

    input_image_path = args.input

    predict(input_image_path)
