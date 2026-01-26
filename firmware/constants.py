# Constants
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_PROMPT = "Briefly describe this in 20 words or less."
MESSAGE_DISPLAY_TIME = 7
ERROR_DISPLAY_TIME = 2
PROMPT_MODES = {
    "shutter": ["Briefly describe this in 20 words or less.", "Providing a brief description of this image."],
    "up": ["What objects or items do you see in this image? List them. Do not say anything else.", "Listing the objects or items in this image."],
    "down": ["Describe the mood or atmosphere of this scene.  Do not say anything else.", "Describing the mood or atmosphere of this scene."],
    "left": ["How do you use this item/tool? Be direct and specific. Do not say anything else.", "Explaining how to use this item or tool."],
    "right": ["Craft a creative story based on this image in under 100 words.", "Creating a story or scenario based on this image."], 
    "select": ["Identify any text visible in this image. Do not say anything else.", "Listing any visible text in this image."],
    "ok": ["What is the main subject or focus of this image?", "Describing the main subject or focus of this image."]
}