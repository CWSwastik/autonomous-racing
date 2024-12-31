import tensorflow as tf
import numpy as np

class LiteModel:
    def __init__(self, model_path):
        self.interpreter = tf.lite.Interpreter(model_path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predict(self, input_data, verbose=0):
        input_data = input_data.astype(np.float32)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        return self.interpreter.get_tensor(self.output_details[0]['index'])

def convert_to_lite_model(model_path, lite_model_path):
    model = tf.keras.models.load_model(model_path)
    model.export('saved_model_dir')

    converter = tf.lite.TFLiteConverter.from_saved_model('saved_model_dir')
    tflite_model = converter.convert()

    with open(lite_model_path, 'wb') as f:
        f.write(tflite_model)

if __name__ == '__main__':
    convert_to_lite_model('neural_net_model.h5', 'model.tflite')