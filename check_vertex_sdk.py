
try:
    from vertexai.preview.vision_models import VideoGenerationModel
    print("VideoGenerationModel found")
except ImportError:
    print("VideoGenerationModel NOT found")

try:
    from vertexai.preview.vision_models import ImageGenerationModel
    print("ImageGenerationModel found")
except ImportError:
    print("ImageGenerationModel NOT found")
