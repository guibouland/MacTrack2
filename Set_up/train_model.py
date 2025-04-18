from kartezio.apps.segmentation import create_segmentation_model
from kartezio.endpoint import EndpointThreshold
from kartezio.dataset import read_dataset
from kartezio.training import train_model


DATASET = "./dataset"
OUTPUT = "./models"


generations = 1000
_lambda = 5
frequency = 5
rate = 0.1
print(rate)
model = create_segmentation_model(
    generations,
    _lambda,
    inputs=3,
    nodes=30,
    node_mutation_rate=rate,
    output_mutation_rate=rate,
    outputs=1,
    fitness="IOU",
    endpoint=EndpointThreshold(threshold=4)
)

dataset = read_dataset(DATASET)
elite, a = train_model(model, dataset, OUTPUT, callback_frequency=frequency)