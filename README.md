# Real-Time NJ Transit Departure Board

This project fetches real-time bus departure data from the NJ Transit API, processes it, and displays it on an interactive web dashboard. The goal is to aid in the development of the real world bus terminal departure boards, showing real departures over varying time frames and experimenting with layout to provide the clearest information to passengers in a hurry.

---

## Live Demo

You can view the live dashboard here:
**[https://njt-departure-board.streamlit.app/](https://njt-departure-board.streamlit.app/)**

---

## Tech Stack & Architecture

This project uses a modern, cloud-native data stack to create a robust and automated system.

### Tech Stack

| Component | Technology |
| :--- | :--- |
| **Data Ingestion** | Python (`requests`) |
| **Transformation** | Python (`polars`, `pydantic`) |
| **Database** | Postgres (Neon - Serverless) |
| **Dashboard** | Streamlit |
| **Containerization** | Docker |

### Architecture

The data flows through the system as follows:

1.  **User Trigger**: When a user visits or refreshes the dashboard, the application triggers the data pipeline.
2.  **ETL Pipeline**: 
    * **Extract**: Fetches real-time departure data from the NJ Transit API.
    * **Transform**: Validates the data with Pydantic and transforms it into a clean, structured format using Polars.
    * **Load**: Connects to a remote **Postgres** database hosted on Neon and performs an idempotent insert, only adding new, unique departure records.
3.  **Dashboard**: The **Streamlit** application queries the Postgres database to fetch and display the latest departure data, showing upcoming departures for each route.

---

## Running the Project Locally

To run this project on your local machine, please follow these steps.

### Prerequisites

* Git
* Python 3.10+
* Docker Desktop

### Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/njt-departure-board.git](https://github.com/your-username/njt-departure-board.git)
    cd njt-departure-board
    ```

2.  **Create a `.env` file:**
    Create a file named `.env` in the root of the project and add your credentials. It should look like this:
    ```
    # .env
    NJT_USERNAME="your_njt_username"
    NJT_PASSWORD="your_njt_password"
    DATABASE_URL="your_neon_postgres_connection_string"
    ```

3.  **Launch the dashboard:**
    This command will build the Docker image and start the Streamlit application.
    ```bash
    docker-compose up
    ```

4.  **View the dashboard:**
    Open your web browser and navigate to **http://localhost:8501**.
