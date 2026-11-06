# PedSafe frontend

Demonstration website for **Urban Pedestrian Risk Prediction and Conflict Detection System**.

All numbers, map pins, and conflict rows are sample data. They are not live traffic.

## Run

```bash
cd frontend
npm install
npm run dev
```

Open the local address Vite prints, usually http://localhost:5173.

## Build

```bash
npm run build
```

## Pages

- `/` Home
- `/dashboard` Overview cards and charts
- `/risk` OpenStreetMap zones
- `/conflicts` Filterable conflict table
- `/analytics` Trends, CSV download, and print / save PDF
- `/about` Project, workflow, and team roles

## Later integration

`src/data/sampleData.js` is the only place the screens read records from. A future API can replace those exports and keep the same field names.
