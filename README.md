# GRT Financials Application

GRT Financials Application is a Streamlit-based tool designed to process financial PDF documents and provide insightful responses to predefined and user-specific queries using the OpenAI API. This application leverages LangChain and vector databases for efficient document processing and retrieval.

## Features

- Upload PDF financial documents and process them.
- Ask predefined questions to extract specific financial data from the documents.
- Interact with the documents through a chat interface powered by OpenAI's GPT.
- Maintain a chat history for seamless interaction and reference.

## Installation

### Prerequisites

- Python 3.7 or higher
- Streamlit
- OpenAI API key
- LangChain API key

### Steps

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/grt-financials-application.git
    cd grt-financials-application
    ```

2. Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    Create a `.env` file in the project root and add your OpenAI and LangChain API keys:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    LANGCHAIN_API_KEY=your_langchain_api_key
    LANGCHAIN_PROJECT=your_langchain_project_name
    ```

5. Run the application:
    ```bash
    streamlit run app.py
    ```

## Usage

1. **Upload PDF Documents**: Use the sidebar to upload your PDF financial documents.
2. **Process Documents**: Click on the "Submit & Process" button to analyze the uploaded documents.
3. **Ask Questions**: Enter your query in the text input box to get responses based on the processed documents.
4. **View Responses**: Responses to both predefined and user queries will be displayed in the chat interface.

## Code Overview

### `app.py`

The main application file that sets up the Streamlit interface:
- Upload PDF files.
- Process the documents and generate responses.
- Display chat history.

### `model.py`

Contains the core functions for:
- Loading and processing PDF documents.
- Splitting text into manageable chunks.
- Storing and retrieving data from a vector database.
- Interacting with the OpenAI API to generate responses.

## Environment Variables

Ensure the following environment variables are set:

- `OPENAI_API_KEY`: Your OpenAI API key.
- `LANGCHAIN_API_KEY`: Your LangChain API key.
- `LANGCHAIN_PROJECT`: Your LangChain project name.

## Contributing

We welcome contributions! Please fork the repository and create a pull request with your changes. Ensure your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [OpenAI](https://openai.com/)
- [LangChain](https://www.langchain.com/)
- [pysqlite3](https://github.com/
