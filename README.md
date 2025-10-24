# AITruthGuard Project

## 1. Project Goal

This project aims to develop an AI-powered "Truth Guard." Its primary goal is to analyze user queries or claims, evaluate their accuracy based on an existing knowledge base (dataset), and provide relevant information. The project focuses on preventing the spread of misinformation and providing reliable information to users.

## 2. About the Dataset

The project utilizes a dataset composed of news articles. This dataset includes both genuine (True) and fake (Fake) news examples. The content of the dataset is used to train natural language processing (NLP) models and to classify the accuracy of claims.

*   **Dataset Content:** News headlines, texts, and corresponding labels (true/fake).
*   **Project Topic:** Misinformation detection and verification.

## 3. Methods Used

This project employs a Retrieval-Augmented Generation (RAG) architecture. This architecture enables a language model (e.g., Gemini) to retrieve relevant information from an external knowledge base (our dataset) to generate more accurate and contextually appropriate responses.

*   **Embedding:** Text embeddings (vector representations) are created using the `sentence-transformers` library.
*   **Vector Database:** The generated embeddings are indexed using FAISS (Facebook AI Similarity Search) for fast retrieval and similarity comparisons.
*   **Language Model:** Google's Gemini API is used to generate responses to user queries.

## 4. Achieved Results

(This section will contain specific results obtained during the project's development phase, such as model performance metrics, accuracy rates, etc. A general summary is provided for now.)

The project demonstrates the potential to classify the accuracy of news texts with a high success rate and to respond to user queries with relevant and accurate information. Thanks to the RAG architecture, the model's access to up-to-date and specific information has been enhanced.

## 5. Code Execution Guide

To run the project locally, follow these steps:

1.  **Create a Python Virtual Environment:**
    ```bash
    python -m venv .venv
    ```
2.  **Activate the Virtual Environment:**
    *   Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
3.  **Install Required Libraries:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set Up API Keys:**
    Create a `.env` file in the project root and add your Google Gemini API key in the following format:
    ```
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    ```
    Also, if used, add your news API key:
    ```
    NEWS_API_KEY=YOUR_NEWS_API_KEY
    ```
5.  **Run the Backend Server (Local):**
    ```bash
    uvicorn backend.server:app --host 0.0.0.0 --port 8000
    ```
    This command will start the FastAPI backend server.

## 6. Solution Architecture

The project uses a RAG (Retrieval-Augmented Generation) architecture consisting of the following core components:

*   **Data Loader:** Loads and processes the news dataset (true and fake news).
*   **Embedder:** Uses `sentence-transformers` to convert news texts and user queries into embeddings, representing them in a vector space.
*   **Vector Database:** Stores the created embeddings in a FAISS index for fast searching and similarity comparisons.
*   **Language Model:** Google's Gemini API is used to generate responses to user queries by retrieving relevant news from the FAISS index.
*   **FastAPI Backend:** Provides RESTful API endpoints that communicate with the frontend and offer RAG chatbot functionality.
*   **Frontend:** Provides the user interface and interacts with the backend.

## 7. Web Interface & Product Guide

**Frontend Deploy Link (GitHub Pages):** [https://damlalper.github.io/AITruthGuard/](https://damlalper.github.io/AITruthGuard/)

**Backend Deploy Link (Render):** [https://aitruthguard-backend.onrender.com](https://aitruthguard-backend.onrender.com)

**Workflow and Testing:**

1.  Access the web interface by clicking on the frontend deploy link above.
2.  The interface will feature a text input area and a "Ask" or "Verify" button.
3.  Type a claim you wish to verify or a question you want to ask into the text input area.
4.  Click the button.
5.  The backend will process your query, find relevant news articles, and generate a response using the Gemini model.
6.  The response will be displayed in the interface. This response may include information about the claim, a confidence level, and relevant news sources.

(Screenshots/video demonstration can be added here.)

## 8. Backend Deployment on Render

To deploy the FastAPI backend to Render, follow these steps:

1.  **Create a Render Account:** If you don't have one, sign up at [Render.com](https://render.com/).
2.  **Create a New Web Service:**
    *   Log in to your Render dashboard.
    *   Click on the "New" button and select "Web Service."
3.  **Connect to GitHub:**
    *   Connect your GitHub repository: `https://github.com/damlalper/AITruthGuard`.
    *   Ensure Render has access to your repository.
4.  **Configure the Service:**
    *   **Name:** Choose a unique name for your service (e.g., `aitruthguard-backend`).
    *   **Region:** Select a region geographically close to your users.
    *   **Branch:** Set to `master`.
    *   **Root Directory:** Leave this field empty (as your `Procfile` is in the root of the repository).
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn backend.server:app --host 0.0.0.0 --port $PORT`
5.  **Set Environment Variables:**
    *   Go to the "Environment" section of your Render service settings.
    *   Add the following environment variables with your actual API keys:
        *   `GEMINI_API_KEY`: Your Google Gemini API key.
        *   `NEWS_API_KEY`: Your News API key (if applicable).
    *   **Important:** These keys should NOT be committed to your GitHub repository.
6.  **Deploy:**
    *   Click "Create Web Service" or "Deploy" to start the deployment process.
    *   Monitor the deployment logs on Render. The service should now start successfully due to the lazy loading implementation.
7.  **Obtain Backend URL:**
    *   Once deployed, Render will provide a public URL for your backend API (e.g., `https://your-service-name.onrender.com`).
8.  **Update Frontend:**
    *   Ensure your frontend (`index.html` on your `gh-pages` branch) is updated to make API calls to this new Render backend URL. (This step has already been completed by the agent.)