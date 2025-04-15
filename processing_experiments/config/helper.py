"""
    Helper functions associated with Presidio configuration
"""
from pprint import pprint
from transformers import AutoModelForTokenClassification
from transformers import pipeline

"""
    Returns the transfomer entities that are classified by the respective model
    
    Needed to perform the presidio entity mappping
"""
def get_transfomer_labels(model_name : str) -> str:
    """
    Returns the labels that the model is predicting

    Args:
        model_name (str): Offical transformer-model name from Huggingface

    Returns:
        str: Labels (PER, ORG, etc.)
    """
    model = AutoModelForTokenClassification.from_pretrained(model_name)
    return model.config.id2label

def get_transfomer_prediction(model_name: str, text: str) -> str:
    """
    Runs the model in a ner pipeline to predict labels
    
    Args:
        model_name (str): Offical transformer-model name from Huggingface
        text (str): Text where the NER entities are predicted
        
    Returns:
        str: Model prediction
    """
    pipe = pipeline("ner", model=model_name, aggregation_strategy="simple")
    return pipe(text)
    
    
if __name__ == "__main__":
    models = ["iiiorg/piiranha-v1-detect-personal-information"]
    text = "My name is George Cloney. My password is LOL. I live in Innsbruck. My street is Leopoldstreet. I am 32 yeards old."
    for model in models:
        print(f"Entity mappings for {model}\n")
        pprint(get_transfomer_labels(model))
        print(get_transfomer_prediction(model,text))