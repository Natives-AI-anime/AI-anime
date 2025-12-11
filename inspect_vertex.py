
import sys
import vertexai
try:
    import vertexai.preview.vision_models
    print(dir(vertexai.preview.vision_models))
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
