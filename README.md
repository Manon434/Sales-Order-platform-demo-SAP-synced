# GreenPaper Sales Order Management — Live SAP Synchronization

This version keeps the existing GreenPaper Sales Order Management UI and connects its SAP order/approval views to the live SAP endpoints supplied for this project.

## Live SAP sources

- E0003 sales orders: `/zso_apr/SO?sap-client=100&ZNAME11=E0003`
- E0006 sales orders: `/zso_apr/SO?sap-client=100&ZNAME11=E0006`
- Approval/SOA: `/zso_aprd/SOA?sap-client=100`

The browser does **not** call SAP directly. `server.py` is a local proxy so the frontend avoids browser CORS restrictions and SAP credentials stay outside `app.js`.

## What is synchronized

- E0003 and E0006 are fetched from SAP.
- SAP rows are grouped by `VBELN` into one sales order.
- Every `POSNR` remains a line item.
- `MATNR`, `ARKTX`, `KWMENG`, `VRKME`, `NETPR`, `NETWR`, `WERKS`, `AUDAT`, `KUNNR`, `NAME1`, `BSTKD` and relevant approval fields are retained.
- Customers and products returned by SAP are created/updated locally in the browser's working dataset.
- SOA is matched back to orders by `VBELN` and drives the displayed SAP approval status.
- The UI shows SAP client, SAP employee, approval user/time/code and synchronization state.

## Automatic synchronization

The application synchronizes immediately on startup and every **15 minutes** while the browser tab is open. A **Sync SAP** button is also available for an immediate refresh.

## Run

1. Open Command Prompt in this folder.
2. Run `run_demo.bat` or `python server.py`.
3. Open `http://localhost:8000`.
4. Sign in using an account created by the existing demo signup screen.

Do not double-click `index.html`; the app must be served through `server.py`.

## Optional SAP authentication

If the SAP server requires authentication, set environment variables before starting the server:

```text
SAP_USER=your_user
SAP_PASSWORD=your_password
```

or:

```text
SAP_TOKEN=your_bearer_token
```

You can also override:

```text
SAP_BASE_URL=http://203.112.143.241:8000
SAP_CLIENT=100
SAP_TIMEOUT=30
PORT=8000
```

## Important limitation

The supplied SAP endpoints are read/approval feeds. This version therefore does **not fake creation of a SAP sales order** when a portal order receives its final local approval. The UI marks that capability as not configured instead of inventing a VBELN. A real SAP create/update endpoint (POST/BAPI/OData/RFC) is required before portal-created orders can be written back to SAP.
