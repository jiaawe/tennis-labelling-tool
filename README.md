# Tennis Labelling Tool

This tool is designed to assist in labelling doubles tennis via a Gradio Interface.

## Installation

1. Clone this repository to your local machine:
   ```
   git clone https://github.com/yourusername/tennis-labelling-tool.git
   cd tennis-labelling-tool
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the Tennis Labelling Tool:

1. Navigate to the project directory in your terminal.

2. Run the Gradio app:
   ```
   python3 app.py
   ```

3. Open your web browser and go to the URL provided in the terminal output (usually `http://127.0.0.1:7860`).

4. Use the interface to label your tennis data.

5. After saving the labelled data, use the json post-processing script to transform the raw labels into individual rallies.

6. Navigate to where the labelled data is stored at `~/data/labelled`

7. Create a document which will store the names in separate rows of all the json files you want to transform e.g. `to_label.txt`
   #### **`to_label.txt`**
   ``` 
   labelled_data_1.json
   labelled_data_2.json
   labelled_data_3.json
   ```
8. Navigate to the project directory using your terminal

9. Run the post-processing script:
   ```
   python transform_json.py -f to_label.txt
   ```

## Features

[To be added]

## Contributing

[To be added]