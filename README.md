# WhatsApp Logistics Assistant

A backend system designed to help truck drivers and logistics managers register, organize, retrieve, and share operational information through WhatsApp.

The system combines FastAPI, PostgreSQL, WhatsApp/Meta Webhooks, and OpenAI to transform natural-language messages into structured information that can be persisted and retrieved later.

The main goal is to make operational information easier to record for truck drivers and easier to access and organize for logistics teams.

---

## The Problem

Operational information in logistics is often exchanged through informal conversations, especially when drivers are away from a computer or working with limited time.

This creates several practical problems:

- Information can be recorded inconsistently.
- Important data can be difficult to retrieve later.
- Communication between drivers and logistics management can become fragmented.
- Manually transferring information from conversations into structured systems creates additional work.

The project explores a conversational approach to this problem.

Instead of requiring drivers to navigate a traditional application, the system allows operational information to be registered through a normal WhatsApp conversation.

---

## The Solution

The application acts as a backend assistant between users and the operational data generated during their activities.

A typical interaction follows this flow:

```text
Driver sends a message
        |
        v
WhatsApp / Meta
        |
        v
Meta Webhook
        |
        v
FastAPI
        |
        v
Payload validation
        |
        v
Webhook Service
        |
        +----------------------+
        |                      |
        v                      v
   Application            AI Service
   processing              |
        |                   v
        |              OpenAI API
        |                   |
        +---------+---------+
                  |
                  v
             Use Case
                  |
                  v
             Repository
                  |
                  v
             PostgreSQL
                  |
                  v
          Stored structured data

The stored information can later be retrieved and organized into responses, lists, tables, and reports.

This creates a communication flow where the user can interact with the system naturally while the backend remains responsible for validation, business logic, persistence, and integration with external services.

Architecture

The application follows a layered structure designed to keep HTTP handling, validation, business logic, AI integration, and persistence separated.

                           WhatsApp / Meta
                                  |
                                  | Webhook
                                  v
                         +-----------------+
                         |     Router      |
                         | HTTP interface  |
                         +--------+--------+
                                  |
                                  v
                         +-----------------+
                         |      DTOs       |
                         | Validation/data |
                         +--------+--------+
                                  |
                                  v
                       +---------------------+
                       |   Webhook Service   |
                       | Application flow    |
                       +----------+----------+
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
          +-------------------+       +-------------------+
          |     Use Cases     |       |    AI Service     |
          | Application logic |       |    OpenAI API     |
          +---------+---------+       +---------+---------+
                    |                           |
                    +-------------+-------------+
                                  |
                                  v
                        +-------------------+
                        |    Repository     |
                        | Persistence logic |
                        +---------+---------+
                                  |
                                  v
                        +-------------------+
                        |    PostgreSQL     |
                        | Persistent data   |
                        +-------------------+

The main architectural objective is to prevent unrelated responsibilities from being concentrated in the same component.

The HTTP layer should not contain database logic.

The database layer should not contain business rules.

The AI integration should not be spread throughout the application.

This separation makes the system easier to understand, test, maintain, and evolve.

Request Processing

Each incoming message passes through a defined application flow.

1. Message Reception

WhatsApp/Meta sends an event to the application's webhook endpoint.

FastAPI receives the HTTP request and forwards the payload for processing.

2. Payload Validation

The external payload is converted into application-level data through DTOs.

This creates a boundary between the structure used by Meta and the internal representation used by the application.

External Meta Payload
          |
          v
         DTO
          |
          v
Validated Application Data
3. User and Message Processing

The application identifies the user associated with the incoming message and processes the message according to the application's defined behavior.

This logic is kept outside the HTTP endpoint so the application flow is not directly coupled to the webhook implementation.

4. AI Interpretation

The application communicates with OpenAI through a dedicated AI service.

The AI layer is responsible for interpreting the user's natural-language message according to the application's defined prompt and response structure.

User Message
      |
      v
 AI Service
      |
      v
 OpenAI API
      |
      v
Structured AI Response
      |
      v
Application Processing

The dedicated service isolates the external provider from the rest of the application.

5. Business Processing

The resulting information is passed to the appropriate application flow.

Use cases represent application-specific operations, while services coordinate interactions between different components.

This keeps business rules independent from HTTP concerns and persistence implementation details.

6. Persistence

Repositories encapsulate access to the database.

The application interacts with persistence through repositories instead of accessing database operations directly from business logic.

Application
     |
     v
Repository
     |
     v
PostgreSQL

This keeps persistence concerns isolated and makes the application easier to test.

Main Components
FastAPI

FastAPI is used as the backend framework responsible for exposing the application's HTTP interface and receiving webhook events.

DTOs

DTOs define the data exchanged between external integrations and the application.

They also validate incoming information before it reaches the application logic.

This prevents external payload structures from propagating throughout unrelated parts of the system.

Services

Services coordinate application behavior and interactions between components.

The webhook service, for example, coordinates the processing of incoming messages without placing the entire flow directly inside the HTTP endpoint.

Use Cases

Use cases represent application-specific operations and business flows.

They provide a dedicated place for application behavior to be implemented independently from framework-specific concerns.

Repositories

Repositories encapsulate persistence operations.

The application interacts with database functionality through these components rather than coupling business logic directly to database access.

Current repository responsibilities include user and message persistence.

AI Service

The AI service is responsible for communication with the OpenAI API.

Keeping this integration isolated allows the rest of the application to remain independent from the implementation details of the external AI provider.

Engineering Principles

The project is designed around several backend engineering principles.

Separation of Responsibilities

Each component has a clearly defined responsibility.

HTTP handling, validation, application behavior, AI communication, and persistence are intentionally separated.

Low Coupling

Components interact through defined responsibilities rather than relying heavily on implementation details from unrelated components.

Dependency Injection

Dependencies are provided to components rather than being created directly inside application logic whenever appropriate.

This improves testability and reduces unnecessary coupling.

Encapsulation

Database access and external integrations are contained behind dedicated components so their implementation details do not leak into unrelated parts of the application.

Testability

The system is structured so individual components can be tested in isolation when appropriate and integrated flows can be tested when interactions between components need to be verified.

Maintainability

The architecture is designed to support future changes without requiring unrelated components to be modified unnecessarily.

Testing Strategy

Testing is one of the main engineering concerns of the project.

The objective is to verify not only individual functions but also the behavior of the application when its components interact.

                    Application Tests
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
         Unit Tests   Integration Tests   API Tests
             |             |             |
             v             v             v
          Isolated      Component       HTTP/Application
           behavior      interaction         behavior
Unit Tests

Unit tests verify individual pieces of application behavior in isolation.

Mocks can be used when external dependencies should not participate in the test.

Integration Tests

Integration tests verify the interaction between multiple application components.

This is especially important for flows involving persistence and communication between application layers.

API Tests

API tests verify behavior exposed through HTTP endpoints, including request validation, response behavior, and application flows.

Test Utilities

The project uses:

Mocks
Fixtures
H2
PostgreSQL-based test environments
Unit testing
Integration testing
API testing

The test structure is intended to provide confidence both in individual components and in the behavior of the application as a whole.

Data and Persistence

PostgreSQL is used as the primary persistent database.

The persistence layer is isolated from the application logic through repositories.

Current application data includes information related to users, messages, and operational records.

Users
  |
  +-- Messages
        |
        +-- Operational information

The application is designed to preserve structured information so that data recorded during one interaction can be retrieved and used in later interactions.

External Integrations
WhatsApp / Meta

WhatsApp is the primary communication interface between users and the system.

The application receives events through Meta webhooks and processes incoming messages in the backend.

OpenAI

OpenAI is used to interpret natural-language messages and transform conversational input into structured application behavior.

The integration is isolated behind a dedicated service to prevent the external provider from becoming tightly coupled to the rest of the system.

Technology Stack
Backend
Python
FastAPI
Database
PostgreSQL
SQLAlchemy
Integrations
WhatsApp / Meta
Meta Webhooks
OpenAI API
Testing
Pytest
Unit Testing
Integration Testing
API Testing
Mocks
Fixtures
H2
PostgreSQL test environments
Infrastructure and Tools
Docker
Git
GitHub
Project Structure

The project is organized to keep framework concerns, application behavior, persistence, and integrations separated.

app/
├── routers/
├── services/
├── repositories/
│   ├── usuario/
│   └── mensagem/
├── use_cases/
├── schemas/
├── models/
├── prompts/
├── database.py
└── main.py

tests/
├── unit/
└── integration/

The structure may evolve as the application grows and new requirements are introduced.

Project Status

The core application flow is implemented and functional.

Current capabilities include:

FastAPI backend
PostgreSQL persistence
WhatsApp webhook processing
OpenAI integration
User handling
Message handling
DTO-based validation
Service layer
Repository layer
Use cases
Layered architecture
Automated tests
Docker-based environment
Application documentation

The project is currently being prepared for the final development steps required to move from a development-focused implementation toward a production-ready deployment.

Roadmap

The remaining roadmap includes:

 Authentication and security hardening
 Global exception handler
 Basic application logging
 Production Meta configuration
 Alembic database migrations
 Production deployment
 Final documentation and production hardening
Project Goals

The project has two main goals.

Product Goal

Create a simpler way for truck drivers and logistics managers to register, organize, retrieve, and exchange operational information.

Engineering Goal

Use a real-world application as a practical environment to deepen knowledge in:

Backend architecture
API design
Automated testing
Database persistence
Webhook-based systems
External API integration
AI integration
Dependency management
Security
Deployment
System design
Why This Project Exists

This project is intentionally more than a CRUD application.

It was created as a practical backend engineering environment where architecture, testing, persistence, integrations, and maintainability are treated as part of the product rather than as secondary concerns.

The system is being developed with the intention of evolving from a development project into a backend capable of serving real users and handling real operational information.

Author

Hugo Mendes

Backend Developer focused on Java/Spring Boot and Python/FastAPI, with interests in backend architecture, automated testing, APIs, databases, integrations, and software engineering.

LinkedIn: https://linkedin.com/in/offhugo

GitHub: https://github.com/Offhugo
