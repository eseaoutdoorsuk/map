# eseaoutdoorsuk-map

## Frontend
- Run frontend locally: `cd docs && python -m http.server`
- Configure map authentication on [Stadia](https://client.stadiamaps.com/dashboard).
- Forked to [own domain](https://github.com/eseaoutdoorsuk/map)
- Link to [custom domain](https://eseaoutdoors.uk/map)

## Backend
- Google sheets access from Python following this [tutorial](https://www.datacamp.com/tutorial/how-to-analyze-data-in-google-sheets-with-python-a-step-by-step-guide)
- Google JSON env downloaded from Google Cloud Console then the string `f"'{json.dumps({...})}'"` added to .env variable `GOOGLE_JSON`
- Get started: `pip install -r api/requirements.txt`
- Run backend locally: `python api/app.py`
- Update locations: `python api/update_location_database.py`
- Backend is deployed to [Vercel](https://eseaoutdoorsuk-map.vercel.app/)
- Black: `black api`