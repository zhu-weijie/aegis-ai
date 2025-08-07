# Aegis AI 🛡️

*An AI-Powered Cyber Data Risk & Resilience Platform*

[![CI](https://github.com/zhu-weijie/aegis-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/zhu-weijie/aegis-ai/actions/workflows/ci.yml)

## About The Project

Aegis AI is a demonstration project built to showcase the application of modern AI/ML techniques to solve real-world problems in Cyber Data Risk & Resilience. It provides an API-driven platform to automate the analysis of potential threats, reducing manual toil for security analysts and enabling faster response times.

This project was developed to exhibit proficiency in Python, backend development, AI integration (LLMs), Infrastructure as Code, and CI/CD automation, directly aligning with the skills required for a modern security development role.

## Core Features

-   **AI-Powered Phishing Triage**: Submit email content via an API endpoint. The system uses a Large Language Model (LLM) to assess the phishing risk, provide a justification, and automatically extract structured **Indicators of Compromise (IoCs)** like URLs, domains, and email addresses.

-   **Automated Threat Intelligence Correlation**: Ingest unstructured threat intelligence reports (e.g., security blog posts, vulnerability disclosures). The system uses **Retrieval-Augmented Generation (RAG)** to create an internal knowledge base that can be queried in natural language.

-   **Closed-Loop Threat Enrichment**: The platform automatically correlates IoCs found in new phishing submissions against the internal threat intelligence knowledge base, providing immediate context if an indicator has been seen in previous reports.

## Tech Stack & Architecture

### Application & Data
-   **Backend**: Python 3.12, FastAPI
-   **Database**: PostgreSQL
-   **ORM & Migrations**: SQLAlchemy, Alembic
-   **AI/ML**: LangChain, OpenAI
-   **Containerization**: Docker, Docker Compose

### DevOps & Cloud
-   **Infrastructure as Code**: Terraform
-   **CI/CD**: GitHub Actions
-   **Cloud Provider**: Amazon Web Services (AWS)
-   **Compute**: ECS (Elastic Container Service) with Fargate
-   **Database**: RDS (Relational Database Service)
-   **Container Registry**: ECR (Elastic Container Registry)
-   **Networking**: VPC, Public/Private Subnets, NAT Gateway
-   **Security**: IAM, Secrets Manager, Security Groups

## Local Development Setup

To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/zhu-weijie/aegis-ai.git
    cd aegis-ai
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3.12 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure local environment:**
    -   Copy the example environment file: `cp .env.local.example .env.local`
    -   Fill in the `POSTGRES_*` and `OPENAI_API_KEY` variables in `.env.local`.

5.  **Start the database container:**
    ```bash
    docker compose up -d db
    ```

6.  **Apply database migrations:**
    ```bash
    alembic upgrade head
    ```

7.  **Run the FastAPI application:**
    ```bash
    uvicorn api.main:app --reload
    ```
    The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

The interactive API documentation (via Swagger UI) is available at the `/docs` endpoint when the application is running.

-   `POST /api/v1/analyze/email`: Submit an email for analysis.
-   `GET /api/v1/analyze/email/{analysis_id}`: Retrieve the results of an analysis.
-   `POST /api/v1/threat-intel/ingest`: Ingest a text document into the RAG knowledge base.
-   `POST /api/v1/threat-intel/query`: Ask a question about the ingested threat intelligence.

## Deployment (IaC & CI/CD)

This project is designed for fully automated deployment to AWS.

-   **Infrastructure**: All AWS resources are defined as code using **Terraform** in the `/terraform` directory. This includes networking, databases, container services, and IAM roles.
-   **Continuous Integration**: The `.github/workflows/ci.yml` pipeline automatically runs linting (`ruff`) and formatting (`black`) checks on every push and pull request to the `main` branch.
-   **Continuous Deployment**: The `.github/workflows/cd.yml` pipeline is triggered manually (`workflow_dispatch`). It builds the production Docker image, pushes it to ECR, and updates the ECS service to deploy the new version. It uses a secure OIDC connection, eliminating the need for long-lived AWS secrets in GitHub.

## Next Steps & Current Status

The project has successfully implemented all core features and the full DevOps pipeline. The immediate next step is to resolve the final container startup issue.

-   [x] Initial project setup (FastAPI, Docker)
-   [x] Database integration (PostgreSQL, Alembic)
-   [x] Feature 1: AI Phishing Triage & IoC Extraction
-   [x] Feature 2: RAG Threat Intelligence & Correlation
-   [x] CI Pipeline with GitHub Actions
-   [x] Full AWS infrastructure provisioned with Terraform
-   [x] CD Pipeline with GitHub Actions

## Design Diagrams

### Phishing Analysis Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant API as "FastAPI Endpoint"
    participant DB as "PostgreSQL Database"
    participant Analyzer as "PhishingAnalyzerService"
    participant ThreatIntel as "ThreatIntelService"
    participant VectorStore as "Vector Store (FAISS)"
    participant LLM as "LangChain (LLM)"

    %% Initial Request/Response
    User->>+API: POST /api/v1/analyze/email
    API->>+DB: INSERT new analysis (status='PENDING')
    DB-->>-API: Return new analysis ID
    Note right of API: Background task is scheduled
    API-->>-User: 200 OK (id, status='PENDING')

    %% Background Processing
    rect rgb(235, 245, 255)
        note over API, LLM: The following runs in the background
        API->>+Analyzer: run_phishing_analysis(id, email_data)
        
        %% AI Analysis
        Analyzer->>+LLM: Analyze content for risk & IoCs
        LLM-->>-Analyzer: Return justification, score, and extracted IoCs

        %% Threat Correlation Loop (RAG Pattern)
        loop For each IoC (domain, URL)
            Analyzer->>+ThreatIntel: query_threat_intel(ioc)
            
            %% Step 1: Retrieval
            ThreatIntel->>+VectorStore: Similarity search for IoC
            VectorStore-->>-ThreatIntel: Return relevant document chunks
            
            %% Step 2: Generation
            ThreatIntel->>+LLM: Ask for summary based on chunks
            LLM-->>-ThreatIntel: Return synthesized context
            
            ThreatIntel-->>-Analyzer: Return context string
        end

        %% Final Database Update
        Analyzer->>+DB: UPDATE analysis SET score, iocs, context, status='COMPLETED'
        DB-->>-Analyzer: OK
        deactivate Analyzer
    end
```

### Threat Intelligence RAG Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant API as "FastAPI Endpoint"
    participant RAG_Service as "ThreatIntelService"
    participant VectorStore as "Vector Store (FAISS)"
    participant LLM as "LangChain (LLM)"

    User->>+API: POST /api/v1/threat-intel/query
    API->>+RAG_Service: query_threat_intel(user_question)

    %% Step 1: Retrieval
    rect rgb(230, 255, 230)
        note over RAG_Service, VectorStore: Step 1: Retrieve relevant context
        RAG_Service->>+VectorStore: Similarity search with user_question
        VectorStore-->>-RAG_Service: Return relevant document chunks
    end

    %% Step 2: Augmentation & Generation
    rect rgb(255, 245, 230)
        note over RAG_Service, LLM: Step 2: Augment prompt and Generate answer
        RAG_Service->>+LLM: Send prompt (user_question + retrieved chunks)
        LLM-->>-RAG_Service: Return synthesized answer
    end
    
    RAG_Service-->>-API: Return final answer
    API-->>-User: 200 OK (answer)
```

### Class Diagram

```mermaid
classDiagram
    direction TD

    %% Define the main components and group them by layer/module
    namespace FastAPI_Application {
        class App {
            +main: FastAPI
            +include_router()
        }
    }

    namespace API_v1_Endpoints {
        class AnalysisRouter {
            +POST /analyze/email
            +GET /analyze/email/[id]
        }
        class ThreatIntelRouter {
            +POST /threat-intel/ingest
            +POST /threat-intel/query
        }
    }

    namespace Services {
        class PhishingAnalyzerService {
            +analyze_email_content()
        }
        class ThreatIntelService {
            +ingest_text()
            +query_threat_intel()
        }
    }

    namespace Schemas_Pydantic {
        class EmailAnalysisRequest
        class PhishingAnalysisResult
        class TextIngestionRequest
        class ThreatIntelQueryRequest
    }

    namespace Models_SQLAlchemy {
        class PhishingAnalysis {
            +id: int
            +status: str
            +risk_score: int
            +justification: str
            +iocs: JSON
            +threat_intel_context: JSON
        }
        class Base {
            <<DeclarativeBase>>
        }
    }

    namespace Core {
        class Database {
            +get_db()
        }
    }
    
    namespace External_Libraries {
        class LangChain_OpenAI {
            +ChatOpenAI
            +OpenAIEmbeddings
        }
        class LangChain_Chains {
            +RetrievalQA
        }
    }

    %% Define the relationships between the components
    App --> AnalysisRouter : includes
    App --> ThreatIntelRouter : includes

    AnalysisRouter --> PhishingAnalyzerService : uses
    AnalysisRouter --> Schemas_Pydantic.EmailAnalysisRequest : validates with
    AnalysisRouter --> Schemas_Pydantic.PhishingAnalysisResult : responds with
    AnalysisRouter --> Core.Database : depends on

    ThreatIntelRouter --> ThreatIntelService : uses
    ThreatIntelRouter --> Schemas_Pydantic.TextIngestionRequest : validates with
    ThreatIntelRouter --> Schemas_Pydantic.ThreatIntelQueryRequest : validates with

    PhishingAnalyzerService --> Models_SQLAlchemy.PhishingAnalysis : creates/updates
    PhishingAnalyzerService --> External_Libraries.LangChain_OpenAI : invokes

    ThreatIntelService --> External_Libraries.LangChain_OpenAI : invokes
    ThreatIntelService --> External_Libraries.LangChain_Chains : uses

    Models_SQLAlchemy.PhishingAnalysis --|> Models_SQLAlchemy.Base : inherits from
```

### AWS Infrastructure Diagram

```mermaid
graph TD
    subgraph "Developer Environment"
        Dev(Developer) -- "git push" --> Github(GitHub Repository)
    end

    subgraph "CI/CD Pipeline (GitHub Actions)"
        Github -- "triggers" --> GA(GitHub Actions)
        GA -- "Step 1: Assume Role (OIDC)" --> IAM_GHA(IAM Role for GHA)
        GA -- "Step 2: Build & Push Image" --> ECR["ECR Repository<br>aegis-ai/api"]
        GA -- "Step 3: Deploy New Version" --> ECS_Service["ECS Fargate Service<br>aegis-ai-api-service"]
    end

    subgraph "AWS Cloud (ap-southeast-1)"
        subgraph "VPC (aegis-ai-vpc)"
            subgraph "Public Subnets"
                User(End User) -- "HTTPS:8000" --> IGW(Internet Gateway)
                IGW --> ECS_Service
                NAT(NAT Gateway)
            end

            subgraph "Private Subnets"
                RouteTable_Private(Private Route Table) <--> RDS["RDS PostgreSQL<br>aegis-ai-db"]
                RouteTable_Private -- "routes to" --> NAT
            end

            subgraph "Services & Security"
                Secrets(Secrets Manager)
                CloudWatch(CloudWatch Logs)
                IAM_ECS(IAM Role for ECS Task)
                IAM_GHA
            end

            ECS_Service -- "Runs" --> Task["ECS Task<br>aegis-ai-api-task"]
            Task -- "reads" --> Secrets
            Task -- "writes to" --> CloudWatch
            Task -- "uses" --> IAM_ECS
            Task -- "connects to" --> RDS
            Task -- "outbound via" --> NAT
        end
    end

    %% Styling
    classDef vpc fill:#FFF5E1,stroke:#000,stroke-width:2px;
    classDef public fill:#E6F3FF,stroke:#000;
    classDef private fill:#FFE6E6,stroke:#000;
    classDef security fill:#E6FFE6,stroke:#000;
    classDef cicd fill:#F0E6FF,stroke:#000;
    classDef dev fill:#FFFFFF,stroke:#000;
    class Dev,Github dev;
    class GA,ECR cicd;
    class VPC vpc;
    class IGW,ECS_Service,NAT,User public;
    class RouteTable_Private,RDS private;
    class Secrets,CloudWatch,IAM_ECS,IAM_GHA,Task security;
```
