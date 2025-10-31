CAPTIONING_PROMPT_BETA = """
Caption this image.
Return stictly in json format

Example of reponse:
{
  captions : [ list of most appropriate captions for the given image] 
}

GUIDELINES
For a given image at max you can go for 5 captions
"""
CAPTIONING_PROMPT = """
You are an expert image analysis assistant. Analyze the provided image and generate multiple short, descriptive captions in JSON format.

Return your response as a valid JSON object with this exact structure:

{
  "captions": [
    "A brief description of the main subject",
    "Focus on the action or activity happening",
    "Describe the setting or location",
    "Mention notable colors or visual style",
    "Focus on key details or elements",
    "A creative or poetic interpretation"
  ]
}

Guidelines:
- Keep each caption between 5-15 words
- Be specific and descriptive
- Vary the focus of each caption (subject, action, setting, mood, etc.)
- Use vivid, concrete language
- Be accurate and objective
- Return ONLY valid JSON with no additional text

Analyze the image and provide the JSON output.

Example Of Response 
{
  "captions": [
    "Golden retriever playing in autumn leaves",
    "Dog jumping joyfully through fallen foliage",
    "Backyard scene on a sunny fall day",
    "Playful and energetic outdoor moment",
    "Warm oranges and browns dominate the scene",
    "Pet enjoying seasonal changes in nature",
    "Scattered leaves create colorful ground cover",
    "Pure happiness captured in motion"
  ]
}

"""