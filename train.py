import pandas as pd
from lite import convert_to_lite_model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import load_model

data = pd.read_csv('racing_data.csv')

X = data[['speed', 'dist_front', 'dist_left_15', 'dist_right_15','dist_left_30', 'dist_right_30','dist_left_45', 'dist_right_45', 'dist_left_60', 'dist_right_60', 'dist_left_75', 'dist_right_75', 'dist_left_90', 'dist_right_90']].values  # Input features
y = data[['left_pressed', 'right_pressed', 'down_pressed', 'up_pressed']].values  # Labels

X[:, 1:] = X[:, 1:] / X[:, 1:].max() # Normalize the input features

model = Sequential([
    Dense(8, activation='relu', input_shape=(X.shape[1],)),
    Dense(12, activation='relu'),
    Dense(6, activation='relu'),
    Dense(y.shape[1], activation='sigmoid')  # Output layer
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

model.fit(X, y, epochs=20, batch_size=4, verbose=1)

model.save('neural_net_model.h5')

loss, accuracy = model.evaluate(X, y, verbose=0)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save the model as a TFLite file
convert_to_lite_model('neural_net_model.h5', 'model.tflite')