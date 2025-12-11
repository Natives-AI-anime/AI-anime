
import vertexai.preview.vision_models
for item in dir(vertexai.preview.vision_models):
    if "Model" in item:
        print(item)
