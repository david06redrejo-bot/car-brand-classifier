import os
import sys
import json
import argparse
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import MODELS_DIR, MODEL_PATH, CLASS_INDICES_PATH, IMG_SIZE, BATCH_SIZE

def train_model(data_dir, epochs=20, fine_tune_at=100):
    """
    Trains a CNN (MobileNetV2) for Car Brand Classification.
    """
    print(f"TensorFlow Version: {tf.__version__}")
    print(f"Training on data from: {data_dir}")

    # Data Augmentation for Training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=0.2  # 20% for validation
    )

    print("Loading Training Data...")
    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )

    print("Loading Validation Data...")
    validation_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )

    num_classes = len(train_generator.class_indices)
    print(f"Detected Classes ({num_classes}): {train_generator.class_indices}")

    # Save Class Indices
    os.makedirs(MODELS_DIR, exist_ok=True)
    # Invert to map index -> label
    idx_to_label = {v: k for k, v in train_generator.class_indices.items()}
    with open(CLASS_INDICES_PATH, 'w') as f:
        json.dump(idx_to_label, f, indent=4)
    print(f"Class indices saved to {CLASS_INDICES_PATH}")

    # Base Model: MobileNetV2 (Lightweight, good accuracy)
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=IMG_SIZE + (3,))
    
    # Freeze base model initially
    base_model.trainable = False

    # Custom Head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.2)(x)  # Regularization
    x = Dense(1024, activation='relu')(x)
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    # Compile
    model.compile(optimizer=Adam(learning_rate=0.0001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    # Callbacks
    callbacks = [
        ModelCheckpoint(filepath=str(MODEL_PATH), save_best_only=True, monitor='val_loss', mode='min'),
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    ]

    # Initial Training (Head only)
    print("Starting Initial Training (Head Only)...")
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // BATCH_SIZE,
        epochs=epochs // 2,
        callbacks=callbacks
    )

    # Fine-Tuning
    print("Unfreezing layers for Fine-Tuning...")
    base_model.trainable = True
    
    # Freeze all layers before the `fine_tune_at` layer
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False

    # Recompile with lower learning rate
    model.compile(optimizer=Adam(learning_rate=1e-5),  # Lower LR for fine-tuning
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    print("Starting Fine-Tuning...")
    history_fine = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // BATCH_SIZE,
        epochs=epochs,
        initial_epoch=history.epoch[-1],
        callbacks=callbacks
    )

    print("Training Complete.")
    print(f"Model saved to {MODEL_PATH}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train CNN for Car Brand Detection")
    # Default to data/raw/cars if not specified
    default_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'raw', 'cars')
    
    parser.add_argument("--data_dir", type=str, default=default_data_path, help="Path to training data")
    parser.add_argument("--epochs", type=int, default=20, help="Number of epochs")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_dir):
        print(f"Error: Data directory '{args.data_dir}' does not exist.")
        sys.exit(1)
        
    train_model(args.data_dir, epochs=args.epochs)
