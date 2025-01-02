
import os
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
import tensorflow as tf


def load_images_from_directory(base_path):
    images = []
    labels = []
    class_names = os.listdir(base_path)

    for class_idx, class_name in enumerate(class_names):
        class_path = os.path.join(base_path, class_name)
        if not os.path.isdir(class_path):
            continue

        for img_name in os.listdir(class_path):
            if img_name.lower().endswith('.png'):
                img_path = os.path.join(class_path, img_name)
                try:
                    # Load and convert to RGB in case images are in different formats
                    img = Image.open(img_path).convert('RGB')
                    # Resize to fixed size (e.g., 64x64)
                    img = img.resize((64, 64))
                    # Convert to numpy array and normalize
                    img_array = np.array(img) / 255.0

                    images.append(img_array)
                    labels.append(class_idx)
                except Exception as e:
                    print(f"Error loading {img_path}: {e}")

    return np.array(images), np.array(labels), class_names

def create_simple_model(num_classes):
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(num_classes, activation='softmax')
    ])

    return model

def train_classifier():
    # Load images
    base_path = 'img/classifier'
    X, y, class_names = load_images_from_directory(base_path)

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and compile model
    model = create_simple_model(len(class_names))
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    # Train model
    history = model.fit(X_train, y_train,
                        epochs=50,
                        validation_data=(X_test, y_test),
                        batch_size=32)

    # Evaluate model
    test_loss, test_acc = model.evaluate(X_test, y_test)
    print(f"\nTest accuracy: {test_acc:.4f}")

    return model, class_names

if __name__ == "__main__":
    model, class_names = train_classifier()

    # Save model if needed
    model.save('simple_classifier.h5')

    # Save class names
    with open('class_names.txt', 'w') as f:
        f.write('\n'.join(class_names))
