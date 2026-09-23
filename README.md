# GreenPaper Sales Order Management — Live SAP Integrated

This package contains the complete frontend and backend for the GreenPaper Sales Order Management Portal.

## Folder structure

```text
GreenPaper_Sales_Order_COMPLETE/
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── backend/
│   ├── server.py
│   └── requirements.txt
├── .env.example
├── .gitignore
├── render.yaml
└── run_demo.bat
```

## How SAP integration works

The browser does NOT call the SAP server directly. `backend/server.py` is the backend and SAP proxy.

```text
Browser
   ↓
GreenPaper frontend
   ↓
/api/sap/orders?employee=E0003
/api/sap/orders?employee=E0006
/api/sap/approvals
   ↓
backend/server.py
   ↓
SAP
```

Live SAP sources configured by default:

- E0003: `/zso_apr/SO?sap-client=100&ZNAME11=E0003`
- E0006: `/zso_apr/SO?sap-client=100&ZNAME11=E0006`
- SOA approvals: `/zso_aprd/SOA?sap-client=100`

The app groups SAP order-line records by `VBELN` and keeps every `POSNR` as an individual line item.

## Local setup

1. Copy `.env.example` to `.env`.
2. Put your real SAP password in `.env`. Do not send the password in chat and do not commit `.env`.
3. Open Command Prompt in this project folder.
4. Run:

```cmd
python backend\server.py
```

or double-click `run_demo.bat`.

5. Open:

```text
http://localhost:8000
```

Do NOT double-click `frontend/index.html`, because the app needs the Python backend for the SAP proxy.

## Direct API checks

After the server starts, these URLs show the data returned through the local backend:

```text
http://localhost:8000/api/sap/orders?employee=E0003
http://localhost:8000/api/sap/orders?employee=E0006
http://localhost:8000/api/sap/approvals
http://localhost:8000/api/sap/health
```

## Where SAP data appears in the UI

- **Dashboard:** SAP connection state, E0003/E0006 synchronized order counts and recent sales orders.
- **Sales Orders:** SAP orders are marked with the SAP badge. Use **SAP Orders** to filter them.
- **Order View:** SAP VBELN, customer PO, plant, approval information and every SAP POSNR line item are displayed.
- **Customers:** SAP customers are added/updated from SAP order rows.
- **Products:** SAP materials are added/updated from SAP order rows.
- **Approval Inbox:** SAP approval information is retained on imported orders.

The app performs an immediate SAP synchronization at startup and repeats it every 15 minutes while the browser tab is open. The **Sync SAP** button forces an immediate refresh.

## GitHub

Do not commit `.env`. Commit `.env.example` instead.

```cmd
git init
git add .
git commit -m "Live SAP sales order integration"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

## Render

Create a Render Web Service from the GitHub repository.

Build command:

```text
pip install -r backend/requirements.txt
```

Start command:

```text
python backend/server.py
```

Set these Render environment variables:

```text
SAP_USER=Mmsupport
SAP_PASSWORD=<your real SAP password>
SAP_BASE_URL=http://203.112.143.241:8000
SAP_CLIENT=100
SAP_TIMEOUT=30
```

The included `render.yaml` contains the same deployment configuration and marks the credentials as secret inputs.

## Important limitation

The supplied SAP endpoints are read/approval feeds. This package does not invent a SAP sales-order creation endpoint. Portal-created orders remain local until a real SAP POST/BAPI/OData/RFC create/update interface is supplied by the SAP team.
