# Quick test script with hardcoded parameters
import sys

# Mock the input function to provide test parameters
test_inputs = [
    "IMG_4128.mp4",  # file name
    "1000",          # ROI x1
    "1803",          # ROI y1
    "1200",          # ROI x2
    "2492",          # ROI y2
    "80",            # starting frame
    "95",            # ending frame
]

input_index = 0

def mock_input(prompt):
    global input_index
    if input_index < len(test_inputs):
        value = test_inputs[input_index]
        print(f"{prompt}{value}")
        input_index += 1
        return value
    return ""

# Replace built-in input
__builtins__.input = mock_input

# Now run the main script
exec(open("VideoProcessor.py").read())
