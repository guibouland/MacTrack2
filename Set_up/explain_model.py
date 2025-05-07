import os
import json
import pandas as pd
import numpy as np


class SummaryModel:
    def __init__(
        self, params, fitness, endpoint, mode, nodes, sequence, functions, model_path
    ):
        self.params = params
        self.fitness = fitness
        self.endpoint = endpoint
        self.mode = mode
        self.nodes = nodes
        self.sequence = sequence
        self.functions = functions
        self.model_path = model_path

    def template(self):
        """
        This function returns a formatted string that summarizes the model.
        """
        return f"""
========================================================================
                            MODEL SUMMARY
========================================================================

🔹 Model path:
{self.model_path}

🔹 Fitness:                                     
{self.format_dict(self.fitness)}

🔹 Endpoint:
{self.format_dict(self.endpoint)}

🔹 Mode:
{self.mode}

🔹 Nodes:
{self.format_dataframe(self.nodes)}

=========================================================================
"""

    @staticmethod
    def format_list(lst):
        """List formatting for display."""
        return "\n".join(str(item) for item in lst)

    @staticmethod
    def format_dict(dct):
        """Dictionary formatting for display."""
        return (
            "\n".join(f"{key}: {value}" for key, value in dct.items())
            if isinstance(dct, dict)
            else str(dct)
        )

    @staticmethod
    def format_dataframe(df):
        """Dataframe formatting for display."""
        return df.to_string(index=False) if isinstance(df, pd.DataFrame) else str(df)

    def to_csv(self):
        """This function saves the nodes dataframe to a CSV file. If an index is provided, it appends the index to the filename for uniqueness."""
        folder_name = os.path.basename(self.model_path)
        # only the first part of the hash in folder_name
        folder_name = folder_name.split("-")[0]
        csv_filename = f"nodes_{folder_name}.csv"
        csv_path = os.path.join(os.path.dirname(self.model_path), csv_filename)
        self.nodes.to_csv(csv_path, index=False)
        return f"Nodes saved to {csv_path}"

    def keys(self):
        """
        This function returns the keys of the model.
        """
        return [
            "params",
            "fitness",
            "endpoint",
            "mode",
            "nodes",
            "sequence",
            "functions",
            "model_path",
        ]


def get_function(sequence, functions):
    """
    Extracts the function names from the sequence based on their IDs.

    The functions are from OpenCV and are used to create the model using Kartezio
    (not all OpenCV functions are used). The function ID is the index of the
    function in the list of functions chosen in the Kartezio package.

    Parameters:
        sequence (list): The sequence of the model, following the Kartezio architecture:
            [function_id, c_1, c_2, ..., c_n, p_1, p_2, ..., p_l]
            - function_id: Index of the function in the list of functions.
            - c_i: Connections (n is the number of connections).
            - p_k: Parameters (l is the number of parameters).
        functions (list): The list of functions available in the Kartezio package.

    Returns:
        list: The list of function names corresponding to the function_id in the sequence.
    """
    function_id = [sublist[0] for sublist in sequence]
    function_names = [functions[i] for i in function_id]
    function_names[0], function_names[1], function_names[2], function_names[-1] = (
        "Hue (Input)",
        "Saturation (Input)",
        "Value (Input)",
        "Label (Endpoint)",
    )
    return function_names


def summary_model(model_folder_path):
    """
    This function loads models from all subdirectories in a specified folder and creates summaries.

    Parameters:
    model_folder (str): Path to the folder containing the models. The function will look for subdirectories within this folder.
    """
    current = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(current)
    model_path = os.path.join(model_folder_path, r"models")
    if not os.path.exists(model_path):
        raise ValueError(
            f"Model path {model_path} does not exist. Please check the path."
        )
    subdirectories = [
        d for d in os.listdir(model_path) if os.path.isdir(os.path.join(model_path, d))
    ]

    if len(subdirectories) == 0:
        raise ValueError(
            f"No subdirectories found in {model_path}. Please check the path."
        )

    summaries = []
    for subdir in subdirectories:
        kartezio_model = os.path.join(model_path, subdir)
        elite = os.path.join(kartezio_model, "elite.json")
        if not os.path.exists(elite):
            print(
                f"Warning: elite.json file not found in {kartezio_model}. Skipping this subdirectory."
            )
            continue

        with open(elite, "r") as f:
            elite_data = json.load(f)

        params = pd.DataFrame([elite_data["decoding"]["metadata"]])
        fitness = pd.DataFrame([elite_data["individual"]["fitness"]])
        endpoint = pd.DataFrame([elite_data["decoding"]["endpoint"]])
        endpoint = endpoint.drop(columns=["abbv", "args", "kwargs"])
        mode = pd.DataFrame([elite_data["decoding"]["mode"]])
        functions = elite_data["decoding"]["functions"]
        n_para = elite_data["decoding"]["metadata"]["n_para"]
        n_conn = elite_data["decoding"]["metadata"]["n_conn"]
        sequence = elite_data["individual"]["sequence"]

        if isinstance(sequence, str):
            try:
                sequence = json.loads(sequence)  # Convert JSON string to Python list
            except json.JSONDecodeError:
                raise ValueError("The 'sequence' field is not a valid JSON string.")

        for i in range(len(sequence)):
            if len(sequence[i]) != n_para + n_conn + 1:
                raise ValueError(
                    f"The length of the sequence {i} is not equal to n_para."
                )

        conns = [sublist[1 : n_conn + 1] for sublist in sequence]
        params = [sublist[n_conn + 1 :] for sublist in sequence]

        function_names = get_function(sequence, functions)
        nodes = pd.DataFrame(list(np.arange(1, len(sequence) + 1)), columns=[""])
        nodes["Function"] = function_names
        for i in range(n_conn):
            nodes[f"Conn_{i+1}"] = [conn[i] for conn in conns]
        for i in range(n_para):
            nodes[f"Param_{i+1}"] = [param[i] for param in params]

        res = SummaryModel(
            params, fitness, endpoint, mode, nodes, sequence, functions, kartezio_model
        )
        print(res.template())
        summaries.append(res)

    return summaries
