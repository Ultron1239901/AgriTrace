# 🛡️ AgriTrace Technology Explanation Manual

This document provides a plain-English explanation of the core technical components of the AgriTrace ecosystem: **Polygon Amoy Blockchain**, **Privacy-Aware LangGraph Multi-Agent Chatbot**, **YOLOv8 & PyTorch Vision Transformers (ViT)**, and **Solidity & Web3.py**.

A styled, printable PDF version of this document is available at: [docs/AgriTrace_Tech_Explanation.pdf](file:///d:/Agriculture%20project/docs/AgriTrace_Tech_Explanation.pdf)

---

## 1. Polygon Amoy Blockchain Ledger

### 💡 What is it in simple words?
Think of the blockchain as a **shared public registry book**. 
* Every time a crop is harvested, packaged, and verified, transaction details are written down in this book.
* Once a page in this book is filled out, signed, and stamped, it is permanently sealed.
* No single person can erase, modify, or rip out that page because identical copies of this exact same registry book are held by thousands of independent computers worldwide. It provides absolute trust and tamper-proof history.

### ⚙️ How it works in AgriTrace:
1. When a farmer registers a crop harvest batch, the backend compiles its details (Batch ID, Farmer Name, Crop Type, Harvest Date, GPS coordinates) into a single text string.
2. The server calculates a unique digital fingerprint of this string using the **SHA-256** hashing algorithm.
3. This fingerprint is uploaded to our smart contract on the **Polygon Amoy testnet** blockchain.
4. When a buyer scans the QR code on a crop card, the backend re-calculates the fingerprint from the current database values and pulls the registered fingerprint from the Polygon blockchain.
5. If someone attempts to falsify or tamper with the database entry (e.g. changing the crop name from "Tomato" to "Carrot"), the newly computed fingerprint will mismatch the blockchain copy, triggering a **TAMPERED** alarm on the buyer's screen.

---

## 2. Privacy-Aware LangGraph Multi-Agent Chatbot

### 💡 What is it in simple words?
Imagine you have a group of specialized agricultural consultants sitting in a room:
* One expert handles weather forecasts.
* One expert monitors market mandi prices.
* One expert scans leaf diseases.
* One expert checks blockchain audits.
* One expert reads general farming handbooks.

Instead of talking to them one-by-one, you talk to the **Supervisor** (the manager). The supervisor listens to your query, routes it to the correct experts, collects their answers, and synthesizes them into one final, coherent advisory report. This multi-step workflow is orchestrated using **LangGraph**.

### ⚙️ Privacy-Aware Integrity:
To protect farmer safety and land coordinates, the LangGraph system is built with **privacy rules**:
* If a buyer asks about a crop batch, the weather and RAG agents automatically sanitize coordinates.
* Instead of returning the exact latitude/longitude coordinates (which could expose the farmer's property bounds), the chatbot filters the coordinates to show only the fuzzed village or district name, ensuring public transparency without violating location privacy.

---

## 3. YOLOv8 & Vision Transformers (ViT)

### 💡 What are they in simple words?
These are the **eyes** of AgriTrace. They allow the server to "see", detect, and diagnose crop photos uploaded by farmers.

### ⚙️ How they work in the diagnostic pipeline:
1. **YOLOv8 (You Only Look Once v8):** This is a high-speed object detection model. When a photo is uploaded, YOLOv8 scans the image, locates the leaves or crops, and draws a bounding box around them. This filters out background noise (like soil, hands, or weeds).
2. **ViT (Vision Transformer):** Once YOLOv8 extracts the leaf patch, the Vision Transformer (built on PyTorch) inspects it. Similar to how language transformers analyze sentences word-by-word, ViT analyzes the leaf image grid patch-by-patch. It identifies fine-grained textures and spots to diagnose diseases (e.g. *Late Blight, Early Blight*) with over 90% confidence.
3. **Multimodal Verification:** To prevent farmers from naming a crop batch "Carrot" but uploading an image of a tomato leaf or random items, the backend runs a multimodal visual validation test. If the image visual contents do not match the entered crop type, it blocks registration and throws an `HTTP 400 Bad Request`.

---

## 4. Solidity & Web3.py

### 💡 What are they in simple words?
If the blockchain is a secured registry vault, **Solidity** is the code used to design the lock on the vault door, and **Web3.py** is the secure phone line the backend server uses to dial in and open it.

### ⚙️ How they interact:
* **Solidity Smart Contract:** We write the crop registry logic in a smart contract. It establishes exactly how fingerprints are stored and queried on-chain. Once compiled and deployed to the Polygon Amoy blockchain network, the contract runs autonomously and cannot be modified.
* **Web3.py:** The FastAPI backend is written in Python, while blockchain nodes speak Ethereum JSON-RPC. Web3.py is the Python integration bridge. It formats the backend transaction data, signs it securely using private keys, sends it to the Polygon network RPC gateway, and reads on-chain variables during QR code scans.
