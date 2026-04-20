# Vercel Deploy Guide

## Files added

- `api/index.py`: entrypoint FastAPI untuk Vercel
- `vercel.json`: config Vercel Functions
- `.python-version`: pin Python `3.12`

## Deploy steps

Jalankan dari folder `ml-stroke-guard`:

```powershell
npm i -g vercel
vercel
```

Untuk production:

```powershell
vercel --prod
```

## Required environment variables

Set di Vercel Project Settings:

- `NEON_URL`
- `JWT_SECRET`

Opsional:

- `PORT`

## Important notes

- Jika repo kamu monorepo, set **Root Directory** ke `ml-stroke-guard`.
- Jalankan migration database terpisah, bukan di Vercel runtime:

```powershell
python database\run_migration.py
```

- FastAPI docs tersedia di `/docs`.
