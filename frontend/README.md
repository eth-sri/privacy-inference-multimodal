This frontend is developed as a [Next.js](https://nextjs.org/) project bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Getting Started

To run the frontend of the labelling tool, you need to have `node.js` installed.

First, install the necessary packages:

```bash
npm i
```

### Secrets

Create an `.env.local` file and fill with:

```.env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
OPENAI_API_KEY=
OPENAI_ORG_ID=
```

Then, run the frontend server:

```bash
npm run dev
```

Open [http://localhost:4000](http://localhost:4000) with your browser to start labelling.

If you have already labelled and want to view your dataset open [http://localhost:4000/labels](http://localhost:4000/labels)

Here you can also hand label whether there is human depiction in the image or not.
