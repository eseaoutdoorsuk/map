# eseaoutdoorsuk-map

## Frontend
- Run frontend locally: `cd docs && python -m http.server`
- Configure map authentication on [Stadia](https://client.stadiamaps.com/dashboard).
- Forked to [own domain](https://github.com/eseaoutdoorsuk/map)

## Backend
- Google sheets access from Python following this [tutorial](https://www.datacamp.com/tutorial/how-to-analyze-data-in-google-sheets-with-python-a-step-by-step-guide)
- Google JSON env downloaded from Google Cloud Console then the string `f"'{json.dumps({...})}'"` added to .env variable `GOOGLE_JSON`
- Run backend locally: `python backend/app.py`
- Backend is deployed to [Vercel](https://eseaoutdoorsuk-map.vercel.app/)