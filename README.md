# Handwritten-M2L: From Image Processing to Deep Learning

Handwritten-M2L is a Python GUI-based application that turns very basic handwritten math equations into LaTeX. The application uses a deep learning model to recognize handwritten symbols, which are extracted using image processing techniques. The symbols are then processed in a sequential manner to generate the corresponding LaTeX expressions.

Please note that this README is a general overview. For more specific details about the project, you can refer to the 
[project document](./G12_Ashraf196280_Farah194233_Jacinta206562.docx)

## Workflow

The project consists of several components that work together to achieve the final result:

1. **Image Preprocessing ([imgPreProcess.py](imgPreProcess.py)):** This script is responsible for processing the input image to be compatible with the neural network model. It extracts the symbols from the image using various image processing techniques.
    - The image is first converted to grayscale and then a median filter is applied to reduce noise.
    - Canny edge detection is used to detect the edges of the symbols.
    - The edges are then dilated to connect the parts of the symbols.
    - Contours are found and bounding boxes are created for each symbol.
    - The symbols are then resized to be compatible with the model.

2. **Deep Learning Model ([model.ipynb](model.ipynb)):** This Jupyter notebook contains the code for training the deep learning model that recognizes the handwritten symbols. The model is trained on a dataset of handwritten symbols and their corresponding labels. The trained model is then saved for later use.
    - The model is a sequential model with multiple convolutional layers, max pooling layers, and dense layers.
    - The model is compiled with the Adam optimizer and the sparse categorical crossentropy loss function.
    - The model is trained on the training data with a batch size of 128 and validated on a validation set.
    - The accuracy and loss of the model are monitored during training.

4. **GUI Application ([gui.py](gui.py)):** This script provides a graphical user interface for the application. It allows the user to either snip an image of a math equation from the screen or load an image from a local folder. The image is then processed and passed to the deep learning model for symbol recognition. The recognized symbols are then converted into LaTeX and displayed in the GUI.

5. **Snipping Tool ([snip.py](snip.py)):** This script is used by the GUI application to snip an image of a math equation from the screen. The snipped image is then processed and passed to the deep learning model for symbol recognition.

## Examples

Here are some examples of the application in action:

- <img
  src="https://github.com/OdyAsh/Handwritten-M2L/blob/main/output1.gif"
  style="display: inline-block; margin: 0 auto; max-width: 400px" />
- <img
  src="https://github.com/OdyAsh/Handwritten-M2L/blob/main/output2.gif"
  style="display: inline-block; margin: 0 auto; max-width: 400px">
- <img
  src="https://github.com/OdyAsh/Handwritten-M2L/blob/main/output3.gif"
  style="display: inline-block; margin: 0 auto; max-width: 400px">
- <img
  src="https://github.com/OdyAsh/Handwritten-M2L/blob/main/output4.gif"
  style="display: inline-block; margin: 0 auto; max-width: 400px">

## Limitations

The current version of the application can only handle very basic expressions. This is because the deep learning model operates on the symbols in a sequential manner, without using Natural Language Processing (NLP) to evaluate the expressions.

## Contributing

We welcome any contributions to the project. Feel free to fork the repository and submit pull requests!

## License

The project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).
