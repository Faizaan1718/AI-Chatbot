## E-commerce Support Chatbot with Contextual Memory

This project is an AI-powered customer support assistant for e-commerce, with short-term conversational memory and FAQ-aware responses. It exposes a Flask REST API and a Streamlit front-end, and can be run locally or via Docker.

### Features

- **Contextual conversation**: remembers recent turns per session.
- **FAQ retrieval**: uses embeddings + vector search to ground answers in an FAQ knowledge base.
- **Local, open-source models**: small conversational model (DialoGPT small by default).
- **REST API**: easy to integrate into existing websites or apps.
- **Modern UI**: Streamlit chat interface with suggested FAQ snippets.

### Project structure

- `data/` – sample e-commerce FAQs and synthetic dialogs, plus scripts to generate them.
- `models/` – training script and saved checkpoints for the conversational model.
- `retrieval/` – FAQ embedding index based on Sentence Transformers + FAISS.
- `memory/` – in-memory session manager for contextual chat.
- `app/` – Flask API (`/chat`, `/reset_session`, `/health`).
- `frontend/` – Streamlit UI.

### Setup (local, without Docker)

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare data**

   ```bash
   python data/prepare_faqs.py
   python data/prepare_dialogs.py
   ```

3. **(Optional) Fine-tune the dialog model**

   ```bash
   python models/train_dialog_model.py
   ```

   This saves a fine-tuned model under `models/checkpoints/ecommerce-support`. If you skip this step, the API falls back to the base DialogGPT model.

4. **Run the Flask API**

   ```bash
   python -m app.main
   ```

   The API will be available at `http://localhost:8000`.

5. **Run the Streamlit UI**

   ```bash
   streamlit run frontend/app.py
   ```

   Open the URL shown in the terminal (usually `http://localhost:8501`).

### API usage

- **POST `/chat`**

  - Request JSON:

    ```json
    {
      "session_id": "optional-string",
      "message": "user question text"
    }
    ```

    - If `session_id` is omitted, the API will create one for you.

  - Response JSON (example):

    ```json
    {
      "reply": "bot response text",
      "suggested_faqs": [
        { "id": "shipping_time", "question": "How long does shipping take?", "answer": "...", "score": 0.85 }
      ],
      "session_id": "generated-or-passed-session-id"
    }
    ```

- **POST `/reset_session`**

  - Request JSON:

    ```json
    { "session_id": "string" }
    ```

  - Clears in-memory history for that session.

- **GET `/health`**

  - Returns `{ "status": "ok" }` when the API is up.

### Running with Docker

1. Build and start both services:

   ```bash
   docker-compose up --build
   ```

2. Access the services:

   - API: `http://localhost:8000`
   - UI: `http://localhost:8501`

The `ui` service is configured to call the `api` service internally, so the chat should work out of the box.

### Integration into your own app

- **Web or mobile frontend**: call the `/chat` endpoint from your front-end code and display a chat widget around it.
- **Back-office tools**: use `/chat` to assist support agents with quick, FAQ-aware draft replies.

You can customize the FAQ data, dialog training data, and model configuration via the scripts and environment variables in `app/config.py`.

