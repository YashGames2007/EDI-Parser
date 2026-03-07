# EDI Parser API (835 / 837 / 834)

A simple FastAPI service that accepts Healthcare EDI files (`.edi`, `.txt`, `.dat`, `.x12`) and returns a parsed JSON structure.

The parser currently:

* Reads the **ISA header**
* Detects **transaction type (835, 837, 834)**
* Splits segments and elements
* Returns structured JSON metadata and segments

This API is intended as the **backend for an EDI visualization and validation system**.

---

# 1. Running the API Locally

## Prerequisites

Make sure you have:

* Python **3.9+**
* pip installed

---

## Step 1 — Clone the Repository

```bash
git clone <your-repo-url>
cd edi-parser-api
```

---

## Step 2 — Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate it.

### Mac / Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## Step 3 — Install Dependencies

```bash
pip install fastapi uvicorn python-multipart
```

`python-multipart` is required for file uploads.

---

## Step 4 — Run the Server

```bash
python api/main.py
```

Explanation:

Server will start running automatically as endpoint is written in the script already.

---

## Step 5 — API Endpoint

Once running, the API will be available at:

```
http://localhost:8000
```

Swagger documentation:

```
http://localhost:8000/docs
```
---

# 2. Using the API with Swagger (Recommended)

FastAPI automatically generates interactive API documentation.

Open:

```
http://localhost:8000/docs
```

You will see the endpoint:

```
POST /parse-edi
```

### Steps

1. Click **POST /parse-edi**
2. Click **Try it out**
3. Upload an EDI file
4. Click **Execute**

Example file formats supported:

```
.edi
.txt
.dat
.x12
```

---

### Example Response

```json
{
  "metadata": {
    "sender_id": "SENDERID",
    "receiver_id": "RECEIVERID",
    "transaction_type": "837 Healthcare Claim"
  },
  "segment_count": 120,
  "segments": [
    {
      "segment_id": "ISA",
      "elements": ["00","..."]
    }
  ]
}
```

---

# 3. Using the API with Postman

Postman is useful for testing APIs outside the browser.

---

## Step 1 — Create Request

Method:

```
POST
```

URL:

```
http://localhost:8000/parse-edi
```

---

## Step 2 — Configure Body

Go to:

```
Body → form-data
```

Add a field:

| Key  | Type | Value                   |
| ---- | ---- | ----------------------- |
| file | File | Upload your `.edi` file |

---

## Step 3 — Send Request

Click:

```
Send
```

Postman will return the parsed JSON response.

---

# 4. Using the API from React

In React you need to send a **multipart/form-data request** using `FormData`.

---

## Example React Upload Component

```javascript
import React, { useState } from "react";

function UploadEDI() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("http://localhost:8000/parse-edi", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    setResult(data);
  };

  return (
    <div>
      <h2>Upload EDI File</h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={handleUpload}>
        Upload
      </button>

      {result && (
        <pre>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default UploadEDI;
```

---

## React Request Flow

```
React Frontend
      ↓
FormData (multipart/form-data)
      ↓
POST /parse-edi
      ↓
FastAPI
      ↓
EDI Parser
      ↓
JSON Response
      ↓
React UI
```

---

# 5. Supported EDI Transactions

The parser currently detects the following transaction types from the `ST` segment:

| Code | Transaction          |
| ---- | -------------------- |
| 837  | Healthcare Claim     |
| 835  | Payment / Remittance |
| 834  | Member Enrollment    |

---

# 6. Example Request

Using `curl`:

```bash
curl -X POST "http://localhost:8000/parse-edi" \
  -H "accept: application/json" \
  -F "file=@example.edi"
```

---

# 7. Project Structure

```
project/
│
├── main.py
├── requirements.txt
└── README.md
```

---

# 8. Future Improvements

Planned enhancements:

* Hierarchical loop detection
* HIPAA validation engine
* Error reporting system
* AI assistant for explaining EDI validation issues
* Interactive tree visualization

---

# 9. Notes

This parser is currently a **basic structural parser** intended for:

* quick inspection
* debugging EDI files
* building visualization tools

It does **not yet implement full HIPAA validation**.
