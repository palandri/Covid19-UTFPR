# -*- coding: utf-8 -*-
"""DenseNetCrossValidation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WXk_cB0hl-ZNJzM6PQVRipRWeUfW9o7W
"""

from src.generic.generic import *
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.layers import AveragePooling2D
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Model
from sklearn.model_selection import train_test_split
import time

def generate_network():
	start_time = time.time()
	print(f"Generating model")
	baseModel = DenseNet121(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
	# construct the head of the model that will be placed on top of the
	# the base model
	headModel = baseModel.output
	headModel = AveragePooling2D(pool_size=(4, 4))(headModel)
	headModel = Flatten(name="flatten")(headModel)
	headModel = Dense(64, activation="relu")(headModel)
	headModel = Dropout(0.5)(headModel)
	headModel = Dense(2, activation="softmax")(headModel)
	# place the head FC model on top of the base model (this will become
	# the actual model we will train)
	model = Model(inputs=baseModel.input, outputs=headModel)
	# loop over all layers in the base model and freeze them so they will
	# *not* be updated during the first training process
	for layer in baseModel.layers:
		layer.trainable = False

	print(f"Finished generating network, time: {time.time() - start_time}s")
	return model


if __name__ == "__main__":
	import uuid
	network_name="densenet"
	unique_id = str(uuid.uuid4())[:5]
	results_path = f"../results/"
	model_path = f"{results_path}saved_models/{network_name}_cross_best_{unique_id}.h5"


	data, lb, labels = load_images("../images")

	#separa 30% do conjunto de treinamento para validacao no final
	(training_x, validation_x, training_y, validation_y) = train_test_split(data,
	                                                                        labels,
	                                                                        test_size=0.30,
	                                                                        stratify=labels)

	model = generate_network()
	history, training_time = train(model,
                                   model_path,
                                   training_x,
                                   training_y,
                                   data,
                                   labels,
                                   n_epochs=1,
                                   kfolds=2)
	generate_training_graphs(history, results_path, network=network_name, unique_id=unique_id)
	report, inference_time = predict(model,
                                     model_path,
                                     validation_x,
                                     validation_y,
                                     network=network_name,
                                     results_path=results_path,
                                     lb=lb,
                                     unique_id=unique_id)
	save_report(results_path, unique_id, report, training_time, inference_time)

