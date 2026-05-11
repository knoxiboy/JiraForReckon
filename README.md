<div align="center">
  <img src="https://via.placeholder.com/1200x300/0f172a/ffffff?text=Jira+Ticket+Evaluator" alt="Jira Ticket Evaluator Banner">
</div>

# Jira Ticket Evaluator 🚀

> **Automated Jira-integrated code evaluation gatekeeper enforcing quality, security, and SDLC best practices.**

[![Live Demo](https://img.shields.io/badge/Live_Demo-Online-00C7B7?style=for-the-badge&logo=vercel)](#)
[![Documentation](https://img.shields.io/badge/Docs-Read-blue?style=for-the-badge&logo=read-the-docs)](#)
[![License](https://img.shields.io/badge/license-MIT-purple.svg?style=for-the-badge)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge&logo=githubactions)](#)

---

## Preview

<div align="center">
  <img src="https://via.placeholder.com/800x400/1e293b/ffffff?text=Evaluation+Dashboard" alt="Dashboard Preview">
  <p><i>The autonomous PR evaluation interface parsing Jira requirements.</i></p>
</div>

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Core Features](#core-features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation Guide](#installation-guide)
- [Environment Variables](#environment-variables)
- [AI/ML/LLM Pipeline](#aimlllm-pipeline)
- [Performance Optimization](#performance-optimization)
- [Security Measures](#security-measures)
- [Roadmap](#roadmap)

---

## Problem Statement

Engineering teams waste thousands of hours manually verifying if a GitHub Pull Request actually satisfies the original product requirements defined in Jira. PR reviews often miss critical acceptance criteria, leading to buggy releases, technical debt, and misaligned features. Existing CI/CD tools check syntax and tests, but cannot intelligently verify **semantic business logic** against project management tickets.

---

## Solution Overview

**Jira Ticket Evaluator** is an AI-powered agentic system that autonomously evaluates whether a GitHub Pull Request satisfies the requirements of a linked Jira ticket. Built for the Hackathon - AI Engineering Track.

By bridging the gap between product management (Jira) and version control (GitHub), the system acts as a smart gatekeeper that provides objective, evidence-based approvals.

- **Intelligent Parsing**: Extracts testable acceptance criteria directly from Jira issues.
- **Diff Analysis**: Evaluates line-level code changes for business logic compliance.
- **Empirical Verification**: Generates and executes validation tests dynamically.

---

## Core Features

### 🕵️‍♂️ Multi-Agent Orchestration
- **What it does**: Coordinates specialized AI agents (Retriever, Parser, Evaluator, Verification, Synthesis) to evaluate code.
- **Why it matters**: Ensures a comprehensive, unbiased, and exhaustive review of the PR.
- **Implementation**: Powered by LangGraph (StateGraph) for deterministic execution state management.

### 🔗 Custom MCP Integrations
- **What it does**: Connects directly to Jira and GitHub via Model Context Protocol (MCP) servers.
- **Why it matters**: Securely and standardly fetches context, diffs, and requirements.
- **Implementation**: Custom stdio transport MCP servers written in Python interacting with Jira/GitHub REST APIs.

### 🧪 Empirical Verification Engine
- **What it does**: Not just reading code, but generating and running Python tests for failed/partial requirements.
- **Why it matters**: Provides cryptographic-level certainty (empirical evidence) rather than just LLM "guessing".
- **Implementation**: Dynamic test execution sandbox.

---

## System Architecture

<div align="center">
  <img src="https://via.placeholder.com/800x400/0f172a/ffffff?text=Architecture+Diagram" alt="Architecture Diagram">
</div>

### Data Flow
1. **Input**: User provides a Jira ticket key and GitHub PR URL via the React Dashboard.
2. **Context Retrieval**: The Retriever Agent connects to MCP servers to fetch Jira data and the PR diff.
3. **Requirement Extraction**: The Parser Agent uses Gemini 2.0 to extract testable acceptance criteria.
4. **Diff Evaluation**: Evaluator Agent assesses each requirement against the code diff with evidence.
5. **Verification**: Verification Agent generates and executes tests for partial/failed requirements.
6. **Synthesis**: Final Pass/Partial/Fail verdict generated with a confidence score.

---

## Tech Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **Frontend** | React, TypeScript, TailwindCSS | High-performance, interactive dashboard |
| **Backend** | Python, FastAPI, Pydantic | Robust API and AI agent orchestration |
| **AI/LLM Engine** | Google Gemini 2.0 Flash | Semantic code and requirement analysis |
| **Orchestration** | LangGraph | State machine agent routing |
| **Integrations** | Custom MCP Servers | Secure bridging to Jira and GitHub |

---

## Project Structure

```bash
jira-ticket-evaluator/
 ┣ backend/            # Agent, tools, MCP integrations
 ┃ ┣ agents/           # Agent definitions (LangGraph nodes)
 ┃ ┣ tools/            # Custom tools and MCP wrappers
 ┃ ┣ state.py          # Shared agent state definition
 ┃ ┗ main.py           # FastAPI server and entry-point
 ┣ tests/              # Custom test generation scripts
 ┣ examples/           # Sample Jira tickets + PRs used for demo
 ┣ docs/               # Architecture diagrams, evaluation reports
 ┗ frontend/           # React dashboard
```

---

## Installation Guide

Get Jira Ticket Evaluator running locally.

### 1. Prerequisites
- Python 3.10+
- Node.js 18+

### 2. Clone & Install
```bash
git clone https://github.com/knoxiboy/JiraForReckon.git
cd JiraForReckon

# Backend Setup
pip install -r requirements.txt

# Frontend Setup
cd frontend
npm install
```

### 3. Run Development Server
```bash
# Start the Backend (from root)
python backend/main.py

# Start the Frontend (from frontend/)
npm run dev
```

---

## Environment Variables

Copy `.env.example` to `.env` in the root directory:

| Variable | Description | Required |
| -------- | ----------- | -------- |
| `GEMINI_API_KEY` | Key for Google Gemini 2.0 | Yes |
| `GITHUB_TOKEN` | Personal Access Token for PR fetching | Yes |
| `JIRA_URL` | e.g. https://your-domain.atlassian.net | Yes |
| `JIRA_USER_EMAIL` | Email associated with Jira account | Yes |
| `JIRA_API_TOKEN` | Atlassian API token | Yes |

---

## AI/ML/LLM Pipeline

The core intelligence of the Jira Ticket Evaluator relies on a robust agentic architecture:
- **Parser Agent**: Employs prompt engineering to map unstructured Jira text into discrete `AcceptanceCriteria` JSON objects.
- **Evaluator Agent**: Performs chunked semantic analysis of the PR diff against each acceptance criteria, mapping code modifications to business logic goals.
- **Synthesis Agent**: Aggregates all sub-agent outputs, producing a final weighted confidence score for the PR's validity.

---

## Performance Optimization

- **Streaming Responses**: The backend streams agent state updates via Server-Sent Events (SSE) to provide real-time UI feedback.
- **Concurrent Tool Calls**: LangGraph executes independent tool calls (e.g., fetching PR diffs and Jira comments) in parallel to reduce evaluation latency.

---

## Security Measures

- **MCP Isolation**: Tool execution is isolated within the Model Context Protocol standards.
- **Token Masking**: API keys for Jira and GitHub are never exposed to the frontend or logged in agent traces.
- **Read-Only Scopes**: The GitHub token only requires `repo:read` scopes, ensuring the agent cannot autonomously modify or merge code without explicit approval.

---

## Roadmap

- [x] Multi-Agent Orchestration with LangGraph
- [x] Custom Jira and GitHub MCP Servers
- [x] React Dashboard for Evaluation Output
- [ ] Auto-Comment on GitHub PRs with Evaluation Verdict
- [ ] Slack/Teams Integration for PR Gatekeeping Notifications
- [ ] Support for GitLab and Linear

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
<div align="center">
<i>Built to bring absolute certainty and precision to your software delivery lifecycle.</i>
</div>
